import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.validates.build_pairs import build_pairs
from utils.validates.build_pairs_n2 import build_pairs_n2
from utils.validates.build_pairs_n3 import build_pairs_n3
from utils.validates.run_validation import (
    METRIC_NAMES,
    build_metrics,
    compute_all_scores,
    prepare_model_data,
    write_metrics,
)


def _collect_metric_values(items: List[Dict[str, Any]], metric_name: str) -> List[float]:
    values: List[float] = []
    for item in items:
        value = item.get(metric_name)
        if value is None or not math.isfinite(value):
            continue
        values.append(float(value))
    return values


def validate_n1n2n3(
    dataset_path: str,
    predicts_dir: str,
    output_path: str,
    output_n1: str | None = None,
    output_n2: str | None = None,
    output_n3: str | None = None,
) -> None:
    print("Validacao N1+N2+N3 iniciada.", flush=True)

    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset: Dict[str, Any] = json.load(file)

    n1_model_data = prepare_model_data(
        dataset, predicts_dir, build_pairs, "generate_n1n2n3", label="N1"
    )
    n2_model_data = prepare_model_data(
        dataset, predicts_dir, build_pairs_n2, "generate_n1n2n3", label="N2"
    )
    n3_model_data = prepare_model_data(
        dataset, predicts_dir, build_pairs_n3, "generate_n1n2n3", label="N3"
    )
    compute_all_scores([n1_model_data, n2_model_data, n3_model_data])

    n1_metrics = build_metrics(n1_model_data, level="n1")
    n2_metrics = build_metrics(n2_model_data, level="n2")
    n3_metrics = build_metrics(n3_model_data, level="n3")

    combined_models: Dict[str, Any] = {}
    combined_averages: Dict[str, Any] = {}
    n1_models: Dict[str, Any] = n1_metrics.get("models", {})
    n2_models: Dict[str, Any] = n2_metrics.get("models", {})
    n3_models: Dict[str, Any] = n3_metrics.get("models", {})

    for model in sorted(set(n1_models.keys()) | set(n2_models.keys()) | set(n3_models.keys())):
        n1_items = n1_models.get(model, {}).get("items", [])
        n2_items = n2_models.get(model, {}).get("items", [])
        n3_items = n3_models.get(model, {}).get("items", [])
        merged_items = n1_items + n2_items + n3_items

        averages: Dict[str, float | None] = {}
        for metric_name in METRIC_NAMES:
            values = _collect_metric_values(merged_items, metric_name)
            averages[metric_name] = sum(values) / len(values) if values else None

        combined_models[model] = {"counts": len(merged_items), "items": merged_items}
        combined_averages[model] = averages

    combined: Dict[str, Any] = {
        "n1": n1_metrics,
        "n2": n2_metrics,
        "n3": n3_metrics,
        "n1n2n3": {"models": combined_models, "averages": combined_averages},
    }

    write_metrics(output_n1, n1_metrics)
    write_metrics(output_n2, n2_metrics)
    write_metrics(output_n3, n3_metrics)
    write_metrics(output_path, combined)

    print(f"Resultado salvo em {output_path}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar N1, N2 e N3 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n1n2n3.json")
    parser.add_argument("--output-n1", default="metrics/validate_n1.json")
    parser.add_argument("--output-n2", default="metrics/validate_n2.json")
    parser.add_argument("--output-n3", default="metrics/validate_n3.json")
    args: argparse.Namespace = parser.parse_args()

    validate_n1n2n3(
        args.dataset,
        args.predicts,
        args.output,
        output_n1=args.output_n1,
        output_n2=args.output_n2,
        output_n3=args.output_n3,
    )
