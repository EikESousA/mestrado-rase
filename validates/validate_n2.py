import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.validates.build_pairs_n2 import build_pairs_n2
from utils.validates.run_validation import run_validation


def validate_n2(dataset_path: str, predicts_dir: str, output_path: str) -> None:
    run_validation(
        level="n2",
        build_pairs_fn=build_pairs_n2,
        dataset_path=dataset_path,
        predicts_dir=predicts_dir,
        output_path=output_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar N2 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n2.json")
    args: argparse.Namespace = parser.parse_args()

    validate_n2(args.dataset, args.predicts, args.output)
