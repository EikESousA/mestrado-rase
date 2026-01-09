import argparse
import sys
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generates.generate_n3 import generate_n3

MODEL_CONFIG: Dict[str, str] = {
    "llama": "llama3.3:latest",
    "alpaca": "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
    "mistral": "cnmoro/mistral_7b_portuguese:q4_K_M",
    "dolphin": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
    "gemma": "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
    "qwen": "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m",
}


def generate_n1_n2_n3() -> None:
    parser = argparse.ArgumentParser(description="Gerar N3 a partir do N1 N2.")
    parser.add_argument(
        "--model",
        choices=["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"],
        default="mistral",
        help="Modelo base para geracao.",
    )
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)
    parser.add_argument("--log", dest="log_path", default=None)
    args: argparse.Namespace = parser.parse_args()

    if args.model not in MODEL_CONFIG:
        print("Modelo invalido.")
        return

    input_path: str = f"predicts/generate_n1_n2_{args.model}.json"
    output_path: str = f"predicts/generate_n1_n2_n3_{args.model}.json"
    model_id: str = MODEL_CONFIG[args.model]

    if args.input_path:
        input_path = args.input_path
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_n3(
        input_path=input_path,
        output_path=output_path,
        model_id=model_id,
        log_path=args.log_path,
    )


if __name__ == "__main__":
    generate_n1_n2_n3()
