from typing import Tuple

from config.models import MODELS, predict_path


def generate_config(tipo: str, modelo: str) -> Tuple[str, str, str]:
    input_file: str = "dataset.json"
    output_file: str = predict_path(tipo, modelo)
    model: str = MODELS[modelo]
    return input_file, output_file, model
