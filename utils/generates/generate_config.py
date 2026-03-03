from typing import Tuple

from utils.generates.model_registry import resolve_model_id


def generate_config(tipo: str, modelo: str) -> Tuple[str, str, str]:
    if tipo in {"n1", "n2", "n3"}:
        input_file = "predicts/dataset_test.json"
    elif tipo == "n1n2":
        input_file = f"predicts/generate_n1_{modelo}_test.json"
    elif tipo == "n1n2n3":
        input_file = f"predicts/generate_n1n2_{modelo}_test.json"
    else:
        input_file = "predicts/dataset_test.json"

    output_file: str = f"predicts/generate_{tipo}_{modelo}_test.json"
    model: str = resolve_model_id(modelo)

    return input_file, output_file, model
