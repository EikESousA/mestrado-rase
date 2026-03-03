import subprocess
import sys
from pathlib import Path
from typing import List

from utils.app.test_mode_dataset import ensure_test_dataset
from utils.generates.check_ollama_installed import check_ollama_installed
from utils.generates.ensure_model_installed import ensure_model_installed
from utils.generates.model_registry import resolve_model_id
from utils.generates.prepare_model_runtime import prepare_model_runtime
from utils.generates.unload_model import unload_model


def _test_io_paths(n_key: str, model: str, test_dataset_path: str) -> tuple[str, str]:
    predicts_dir = Path("predicts")

    if n_key == "n1":
        input_path = test_dataset_path
        output_path = predicts_dir / f"generate_n1_{model}_test.json"
    elif n_key == "n2":
        input_path = test_dataset_path
        output_path = predicts_dir / f"generate_n2_{model}_test.json"
    elif n_key == "n3":
        input_path = test_dataset_path
        output_path = predicts_dir / f"generate_n3_{model}_test.json"
    elif n_key == "n1n2":
        input_path = str(predicts_dir / f"generate_n1_{model}_test.json")
        output_path = predicts_dir / f"generate_n1n2_{model}_test.json"
    elif n_key == "n1n2n3":
        input_path = str(predicts_dir / f"generate_n1n2_{model}_test.json")
        output_path = predicts_dir / f"generate_n1n2n3_{model}_test.json"
    else:
        input_path = test_dataset_path
        output_path = predicts_dir / f"generate_{n_key}_{model}_test.json"

    return input_path, str(output_path)


def run_generator(n_key: str, models: List[str], test_mode: bool = False) -> None:
    if not check_ollama_installed():
        return

    script_path: Path = Path(__file__).resolve().parents[2] / "generates" / f"generate_{n_key}.py"
    if not script_path.exists():
        print(f"N{n_key[1:]} nao esta disponivel neste menu.")
        return

    test_dataset_path = ensure_test_dataset(
        dataset_path="dataset.json",
        output_path="predicts/dataset_test.json",
        limit=5,
    )

    for model_index, model in enumerate(models):
        model_id: str = resolve_model_id(model)

        if not ensure_model_installed(model, model_id):
            return

        if model_index > 0:
            print("------------------------------------------------------------")
        runtime_env, fallback_process = prepare_model_runtime(model)
        if fallback_process is not None:
            print(
                f"Modelo {model} usara instancia local CPU-only do Ollama "
                "para contornar falha do backend GPU."
            )
        command = [sys.executable, str(script_path), "--model", model]
        input_path, output_path = _test_io_paths(n_key, model, test_dataset_path)
        if n_key in {"n1n2", "n1n2n3"} and not Path(input_path).exists():
            print(f"Arquivo de entrada de teste nao encontrado: {input_path}")
            print("Gere as etapas anteriores em modo teste antes de continuar.")
            if model_id:
                unload_model(model_id, host=runtime_env.get("RASE_OLLAMA_HOST"))
            if fallback_process is not None:
                fallback_process.terminate()
                try:
                    fallback_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    fallback_process.kill()
                    fallback_process.wait(timeout=5)
            continue
        command.extend(["--input", input_path, "--output", output_path])
        subprocess.run(command, check=False, env=runtime_env)
        if fallback_process is not None:
            fallback_process.terminate()
            try:
                fallback_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                fallback_process.kill()
                fallback_process.wait(timeout=5)
        else:
            unload_model(model_id, host=runtime_env.get("RASE_OLLAMA_HOST"))
