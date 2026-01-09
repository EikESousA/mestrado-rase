import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("Executando:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa o pipeline N1 -> N2 -> N3 com o primeiro item do dataset."
    )
    parser.add_argument("--dataset", default="dataset.json")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    first_item = dataset.get("datas", [])[0]
    sample_data = {"counts": 1, "datas": [first_item]}

    model = "llama"
    predicts_target = Path("predicts")
    predicts_target.mkdir(parents=True, exist_ok=True)
    output_path = predicts_target / "generate_test.py"

    temp_dir = Path(tempfile.mkdtemp(prefix="rase_test_"))
    predicts_dir = temp_dir / "predicts"
    metrics_dir = temp_dir / "metrics"
    predicts_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    sample_path = temp_dir / "dataset_sample.json"
    with open(sample_path, "w", encoding="utf-8") as file:
        json.dump(sample_data, file, ensure_ascii=False, indent=2)

    n1_output = predicts_dir / f"generate_n1_{model}.json"
    n2_output = predicts_dir / f"generate_n2_{model}.json"
    n3_output = predicts_dir / f"generate_n3_{model}.json"

    run(
        [
            sys.executable,
            "generates/generate_n1.py",
            "--model",
            model,
            "--input",
            str(sample_path),
            "--output",
            str(n1_output),
        ]
    )
    run(
        [
            sys.executable,
            "generates/generate_n2.py",
            "--model",
            model,
            "--input",
            str(n1_output),
            "--output",
            str(n2_output),
        ]
    )
    run(
        [
            sys.executable,
            "generates/generate_n3.py",
            "--model",
            model,
            "--input",
            str(n2_output),
            "--output",
            str(n3_output),
        ]
    )

    validate_n1_path = metrics_dir / "validate_n1.json"
    validate_n2_path = metrics_dir / "validate_n2.json"
    validate_n3_path = metrics_dir / "validate_n3.json"

    run(
        [
            sys.executable,
            "validates/validate_n1.py",
            "--dataset",
            str(sample_path),
            "--predicts",
            str(predicts_dir),
            "--output",
            str(validate_n1_path),
        ]
    )
    run(
        [
            sys.executable,
            "validates/validate_n2.py",
            "--dataset",
            str(sample_path),
            "--predicts",
            str(predicts_dir),
            "--output",
            str(validate_n2_path),
        ]
    )
    run(
        [
            sys.executable,
            "validates/validate_n3.py",
            "--dataset",
            str(sample_path),
            "--predicts",
            str(predicts_dir),
            "--output",
            str(validate_n3_path),
        ]
    )

    with open(n3_output, "r", encoding="utf-8") as file:
        result = json.load(file)

    with open(validate_n1_path, "r", encoding="utf-8") as file:
        metrics_n1 = json.load(file)
    with open(validate_n2_path, "r", encoding="utf-8") as file:
        metrics_n2 = json.load(file)
    with open(validate_n3_path, "r", encoding="utf-8") as file:
        metrics_n3 = json.load(file)

    final_result = {
        "counts": result.get("counts", 0),
        "datas": result.get("datas", []),
        "time": result.get("time", 0.0),
        "metrics": {
            "n1": metrics_n1,
            "n2": metrics_n2,
            "n3": metrics_n3,
        },
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(final_result, file, ensure_ascii=False, indent=2)

    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
