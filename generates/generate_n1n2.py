import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generates.generate_n2 import generate_n2
from utils.generates.generate_config import generate_config
from utils.generates.model_registry import MODEL_ALIASES, MODEL_NAMES

def generate_n1n2() -> None:
    parser = argparse.ArgumentParser(description="Gerar operadores N2 a partir do N1.")
    parser.add_argument(
        "--model",
        choices=MODEL_NAMES,
        default="mistral",
        help="Modelo base para geracao.",
    )
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)
    parser.add_argument("--log", dest="log_path", default=None)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--top-p", dest="top_p", type=float, default=0.9)
    parser.add_argument("--top-k", dest="top_k", type=int, default=40)
    parser.add_argument("--repeat-penalty", dest="repeat_penalty", type=float, default=1.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-ctx", dest="num_ctx", type=int, default=None)
    parser.add_argument("--num-predict", dest="num_predict", type=int, default=None)
    parser.add_argument("--strict-json", action="store_true")
    parser.add_argument("--no-json-format", action="store_true")
    args: argparse.Namespace = parser.parse_args()

    if args.model not in MODEL_ALIASES:
        print("Modelo invalido.")
        return

    input_path, output_path, model_id = generate_config("n1n2", args.model)
    input_path = str(input_path)
    output_path = str(output_path)
    model_id = str(model_id)
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_n2(
        input_path=input_path,
        output_path=output_path,
        model_id=model_id,
        model_name=args.model,
        log_path=args.log_path,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        repeat_penalty=args.repeat_penalty,
        seed=args.seed,
        num_ctx=args.num_ctx,
        num_predict=args.num_predict,
        strict_json=args.strict_json,
        use_json_format=not args.no_json_format,
        stage_label="N1N2",
    )


if __name__ == "__main__":
    generate_n1n2()
