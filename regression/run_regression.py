import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.generates.model_registry import MODEL_NAMES


VALID_MODELS: List[str] = MODEL_NAMES.copy()


def _run(command: List[str]) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def _parse_models(raw_models: str) -> List[str]:
    normalized = raw_models.strip().lower()
    if normalized == "all":
        return VALID_MODELS.copy()

    values = [value.strip().lower() for value in normalized.split(",") if value.strip()]
    if not values:
        raise ValueError("Nenhum modelo informado.")

    invalid = [model for model in values if model not in VALID_MODELS]
    if invalid:
        raise ValueError(f"Modelos invalidos: {', '.join(invalid)}")

    unique: List[str] = []
    seen = set()
    for model in values:
        if model in seen:
            continue
        seen.add(model)
        unique.append(model)
    return unique


def _refresh_regression_dataset(
    source_dataset_path: Path,
    cases_path: Path,
    regression_dataset_path: Path,
) -> None:
    with source_dataset_path.open("r", encoding="utf-8") as file:
        source_dataset = json.load(file)
    with cases_path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    source_items = source_dataset.get("datas", [])
    indices = cases.get("indices", [])
    if not isinstance(indices, list) or not all(isinstance(index, int) for index in indices):
        raise ValueError("Arquivo de casos invalido: 'indices' deve ser lista de inteiros.")

    invalid = [index for index in indices if index < 0 or index >= len(source_items)]
    if invalid:
        raise ValueError(
            "Indices fora do dataset de origem: "
            + ", ".join(str(index) for index in invalid)
        )

    subset = {
        "counts": len(indices),
        "datas": [source_items[index] for index in indices],
    }

    regression_dataset_path.parent.mkdir(parents=True, exist_ok=True)
    with regression_dataset_path.open("w", encoding="utf-8") as file:
        json.dump(subset, file, ensure_ascii=False, indent=2)

    print(
        "Dataset de regressao atualizado com "
        f"{len(indices)} casos em {regression_dataset_path}.",
        flush=True,
    )


def _build_generation_args(args: argparse.Namespace) -> List[str]:
    common = [
        "--temperature",
        str(args.temperature),
        "--top-p",
        str(args.top_p),
        "--top-k",
        str(args.top_k),
        "--repeat-penalty",
        str(args.repeat_penalty),
        "--seed",
        str(args.seed),
    ]
    if args.num_ctx is not None:
        common.extend(["--num-ctx", str(args.num_ctx)])
    if args.num_predict is not None:
        common.extend(["--num-predict", str(args.num_predict)])
    return common


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Executa regressao fixa (N1, N2, N3 e validacoes) em conjunto reduzido."
    )
    parser.add_argument(
        "--models",
        default="llama3.1",
        help="Modelo(s): ex. llama3.1 ou llama3.1,mistral ou all",
    )
    parser.add_argument("--dataset", default="regression/dataset_regression.json")
    parser.add_argument("--predicts-dir", default="predicts/regression")
    parser.add_argument("--metrics-dir", default="metrics/regression")
    parser.add_argument("--source-dataset", default="dataset.json")
    parser.add_argument("--cases", default="regression/cases.json")
    parser.add_argument("--refresh-dataset", action="store_true")
    parser.add_argument("--skip-generate", action="store_true")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--top-p", dest="top_p", type=float, default=0.9)
    parser.add_argument("--top-k", dest="top_k", type=int, default=40)
    parser.add_argument("--repeat-penalty", dest="repeat_penalty", type=float, default=1.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-ctx", dest="num_ctx", type=int, default=None)
    parser.add_argument("--num-predict", dest="num_predict", type=int, default=None)
    parser.add_argument("--no-strict-json", action="store_true")
    args = parser.parse_args()

    models = _parse_models(args.models)
    dataset_path = Path(args.dataset)
    predicts_dir = Path(args.predicts_dir)
    metrics_dir = Path(args.metrics_dir)

    if args.refresh_dataset:
        _refresh_regression_dataset(
            source_dataset_path=Path(args.source_dataset),
            cases_path=Path(args.cases),
            regression_dataset_path=dataset_path,
        )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset de regressao nao encontrado: {dataset_path}. "
            "Use --refresh-dataset para recriar a partir de cases.json."
        )

    predicts_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    python = sys.executable
    generation_args = _build_generation_args(args)
    strict_json = not args.no_strict_json

    if not args.skip_generate:
        for model in models:
            n1_output = predicts_dir / f"generate_n1_{model}.json"
            n2_output = predicts_dir / f"generate_n2_{model}.json"
            n3_output = predicts_dir / f"generate_n3_{model}.json"
            n1n2_alias = predicts_dir / f"generate_n1n2_{model}.json"
            n1n2n3_alias = predicts_dir / f"generate_n1n2n3_{model}.json"

            _run(
                [
                    python,
                    "generates/generate_n1.py",
                    "--model",
                    model,
                    "--input",
                    str(dataset_path),
                    "--output",
                    str(n1_output),
                    "--log",
                    str(predicts_dir / f"generate_n1_{model}.log"),
                    *generation_args,
                ]
            )
            n2_command = [
                python,
                "generates/generate_n2.py",
                "--model",
                model,
                "--input",
                str(n1_output),
                "--output",
                str(n2_output),
                "--log",
                str(predicts_dir / f"generate_n2_{model}.log"),
                *generation_args,
            ]
            if strict_json:
                n2_command.append("--strict-json")
            _run(n2_command)

            n3_command = [
                python,
                "generates/generate_n3.py",
                "--model",
                model,
                "--input",
                str(n2_output),
                "--output",
                str(n3_output),
                "--log",
                str(predicts_dir / f"generate_n3_{model}.log"),
                *generation_args,
            ]
            if strict_json:
                n3_command.append("--strict-json")
            _run(n3_command)

            shutil.copyfile(n2_output, n1n2_alias)
            shutil.copyfile(n3_output, n1n2n3_alias)

    if not args.skip_validate:
        _run(
            [
                python,
                "validates/validate_n1.py",
                "--dataset",
                str(dataset_path),
                "--predicts",
                str(predicts_dir),
                "--output",
                str(metrics_dir / "validate_n1.json"),
            ]
        )
        _run(
            [
                python,
                "validates/validate_n2.py",
                "--dataset",
                str(dataset_path),
                "--predicts",
                str(predicts_dir),
                "--output",
                str(metrics_dir / "validate_n2.json"),
            ]
        )
        _run(
            [
                python,
                "validates/validate_n3.py",
                "--dataset",
                str(dataset_path),
                "--predicts",
                str(predicts_dir),
                "--output",
                str(metrics_dir / "validate_n3.json"),
            ]
        )
        _run(
            [
                python,
                "validates/validate_n1n2.py",
                "--dataset",
                str(dataset_path),
                "--predicts",
                str(predicts_dir),
                "--output",
                str(metrics_dir / "validate_n1n2.json"),
                "--output-n1",
                str(metrics_dir / "validate_n1_from_n1n2.json"),
                "--output-n2",
                str(metrics_dir / "validate_n2_from_n1n2.json"),
            ]
        )
        _run(
            [
                python,
                "validates/validate_n1n2n3.py",
                "--dataset",
                str(dataset_path),
                "--predicts",
                str(predicts_dir),
                "--output",
                str(metrics_dir / "validate_n1n2n3.json"),
                "--output-n1",
                str(metrics_dir / "validate_n1_from_n1n2n3.json"),
                "--output-n2",
                str(metrics_dir / "validate_n2_from_n1n2n3.json"),
                "--output-n3",
                str(metrics_dir / "validate_n3_from_n1n2n3.json"),
            ]
        )

    print("Regressao concluida.", flush=True)


if __name__ == "__main__":
    main()
