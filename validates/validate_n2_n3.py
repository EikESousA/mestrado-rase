import argparse
import gc
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List

import gensim.downloader as api
from fuzzywuzzy import fuzz
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

from utils.validates.compute_multilingual_scores import compute_multilingual_scores
from utils.validates.compute_sbert_scores import compute_sbert_scores
from utils.validates.compute_tfidf_scores import compute_tfidf_scores
from utils.validates.compute_wmd_scores import compute_wmd_scores
from utils.validates.load_nilc_model import load_nilc_model
from validates.validate_n2 import build_pairs_n2
from validates.validate_n3 import build_pairs_n3


MODEL_NAMES: List[str] = ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]
METRIC_NAMES: List[str] = [
    "fuzzywuzzy",
    "tfidf",
    "sbert",
    "multilingual",
    "wmd_ft",
    "wmd_nilc",
]


def _collect_metric_values(items: List[Dict[str, Any]], metric_name: str) -> List[float]:
    values: List[float] = []
    for item in items:
        value = item.get(metric_name)
        if value is None or not math.isfinite(value):
            continue
        values.append(float(value))
    return values


def _load_predictions(
    predicts_dir: str,
    model: str,
    debug_enabled: bool,
) -> Dict[str, Any] | None:
    input_path = Path(predicts_dir) / f"generate_n2_n3_{model}.json"
    if not input_path.exists():
        if debug_enabled:
            print(f"Pulando {model}: arquivo nao encontrado.", flush=True)
        return None
    with open(input_path, "r", encoding="utf-8") as file:
        return json.load(file)


def _prepare_model_data_n2(
    dataset: Dict[str, Any],
    predicts_dir: str,
    debug_enabled: bool,
) -> Dict[str, Dict[str, Any]]:
    model_data: Dict[str, Dict[str, Any]] = {}
    for model in MODEL_NAMES:
        predictions = _load_predictions(predicts_dir, model, debug_enabled)
        if predictions is None:
            continue
        print(f"Carregando modelo {model} (N2)...", flush=True)
        pairs = build_pairs_n2(dataset, predictions)
        if debug_enabled:
            print(f"Pares N2 gerados ({model}): {len(pairs)}", flush=True)
        targets = [p["target"] for p in pairs]
        predicted = [p["predicted"] for p in pairs]
        model_data[model] = {
            "pairs": pairs,
            "targets": targets,
            "predicted": predicted,
            "scores": {name: [] for name in METRIC_NAMES},
        }
    return model_data


def _prepare_model_data_n3(
    dataset: Dict[str, Any],
    predicts_dir: str,
    debug_enabled: bool,
) -> Dict[str, Dict[str, Any]]:
    model_data: Dict[str, Dict[str, Any]] = {}
    for model in MODEL_NAMES:
        predictions = _load_predictions(predicts_dir, model, debug_enabled)
        if predictions is None:
            continue
        print(f"Carregando modelo {model} (N3)...", flush=True)
        pairs = build_pairs_n3(dataset, predictions)
        if debug_enabled:
            print(f"Pares N3 gerados ({model}): {len(pairs)}", flush=True)
        targets = [p["target"] for p in pairs]
        predicted = [p["predicted"] for p in pairs]
        model_data[model] = {
            "pairs": pairs,
            "targets": targets,
            "predicted": predicted,
            "scores": {name: [] for name in METRIC_NAMES},
        }
    return model_data


def _compute_scores(
    datasets: List[Dict[str, Dict[str, Any]]],
    debug_enabled: bool,
) -> None:
    for metric_name in METRIC_NAMES:
        if metric_name == "fuzzywuzzy":
            for dataset in datasets:
                for model, data in dataset.items():
                    scores = [
                        fuzz.partial_ratio(t, p) / 100.0
                        for t, p in zip(data["targets"], data["predicted"])
                    ]
                    data["scores"][metric_name] = scores
                    print(f"Modelo {model}: FuzzyWuzzy validado.", flush=True)
            continue
        if metric_name == "tfidf":
            for dataset in datasets:
                for model, data in dataset.items():
                    scores = compute_tfidf_scores(data["targets"], data["predicted"])
                    data["scores"][metric_name] = scores
                    print(f"Modelo {model}: TF-IDF validado.", flush=True)
            continue
        if metric_name == "sbert":
            if debug_enabled:
                print("Carregando modelo SBERT...", flush=True)
            sbert_model: SentenceTransformer = SentenceTransformer(
                "tgsc/sentence-transformer-ult5-pt-small"
            )
            for dataset in datasets:
                for model, data in dataset.items():
                    scores = compute_sbert_scores(sbert_model, data["targets"], data["predicted"])
                    data["scores"][metric_name] = scores
                    print(f"Modelo {model}: SBERT validado.", flush=True)
            del sbert_model
            gc.collect()
            continue
        if metric_name == "multilingual":
            if debug_enabled:
                print("Carregando modelo MULTILINGUAL...", flush=True)
            multilingual_model: SentenceTransformer = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
            )
            for dataset in datasets:
                for model, data in dataset.items():
                    scores = compute_multilingual_scores(
                        multilingual_model,
                        data["targets"],
                        data["predicted"],
                    )
                    data["scores"][metric_name] = scores
                    print(f"Modelo {model}: MULTILINGUAL validado.", flush=True)
            del multilingual_model
            gc.collect()
            continue
        if metric_name == "wmd_ft":
            word_vectors_ft: KeyedVectors | None = None
            try:
                if debug_enabled:
                    print("Carregando modelo WMD_FT...", flush=True)
                word_vectors_ft = api.load("fasttext-wiki-news-subwords-300")
            except Exception as exc:
                print(f"Falha ao carregar WMD_FT: {exc}", flush=True)
            if word_vectors_ft is not None:
                for dataset in datasets:
                    for model, data in dataset.items():
                        scores = compute_wmd_scores(
                            word_vectors_ft,
                            data["targets"],
                            data["predicted"],
                        )
                        data["scores"][metric_name] = scores
                        print(f"Modelo {model}: WMD_FT validado.", flush=True)
                del word_vectors_ft
                gc.collect()
            else:
                for dataset in datasets:
                    for model in dataset:
                        data = dataset[model]
                        data["scores"][metric_name] = [None] * len(data["targets"])
                        print(f"Modelo {model}: WMD_FT indisponivel.", flush=True)
            continue
        if metric_name == "wmd_nilc":
            word_vectors_nilc: KeyedVectors | None = load_nilc_model()
            if word_vectors_nilc is not None:
                for dataset in datasets:
                    for model, data in dataset.items():
                        scores = compute_wmd_scores(
                            word_vectors_nilc,
                            data["targets"],
                            data["predicted"],
                        )
                        data["scores"][metric_name] = scores
                        print(f"Modelo {model}: WMD_NILC validado.", flush=True)
                del word_vectors_nilc
                gc.collect()
            else:
                print(
                    "Modelo NILC nao encontrado em models/cbow_s300.txt ou src/models/cbow_s300.txt.",
                    flush=True,
                )
                for dataset in datasets:
                    for model in dataset:
                        data = dataset[model]
                        data["scores"][metric_name] = [None] * len(data["targets"])
                        print(f"Modelo {model}: WMD_NILC indisponivel.", flush=True)
            continue


def _build_metrics(model_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {"models": {}, "averages": {}}
    for model, data in model_data.items():
        pairs = data["pairs"]
        items: List[Dict[str, Any]] = []
        for i, pair in enumerate(pairs):
            items.append(
                {
                    **pair,
                    "fuzzywuzzy": data["scores"]["fuzzywuzzy"][i]
                    if i < len(data["scores"]["fuzzywuzzy"])
                    else None,
                    "tfidf": data["scores"]["tfidf"][i]
                    if i < len(data["scores"]["tfidf"])
                    else None,
                    "sbert": data["scores"]["sbert"][i]
                    if i < len(data["scores"]["sbert"])
                    else None,
                    "multilingual": data["scores"]["multilingual"][i]
                    if i < len(data["scores"]["multilingual"])
                    else None,
                    "wmd_ft": data["scores"]["wmd_ft"][i]
                    if i < len(data["scores"]["wmd_ft"])
                    else None,
                    "wmd_nilc": data["scores"]["wmd_nilc"][i]
                    if i < len(data["scores"]["wmd_nilc"])
                    else None,
                }
            )

        averages: Dict[str, float | None] = {}
        for metric_name in METRIC_NAMES:
            values = [
                item[metric_name]
                for item in items
                if item[metric_name] is not None and math.isfinite(item[metric_name])
            ]
            averages[metric_name] = sum(values) / len(values) if values else None

        metrics["models"][model] = {
            "counts": len(items),
            "items": items,
        }
        metrics["averages"][model] = averages
    return metrics


def _write_metrics(output_path: str | None, metrics: Dict[str, Any]) -> None:
    if output_path is None:
        return
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)


def validate_n2_n3(
    dataset_path: str,
    predicts_dir: str,
    output_path: str,
    output_n2: str | None = None,
    output_n3: str | None = None,
) -> None:
    env_debug: str = os.getenv("GENERATE_DEBUG", "").strip().lower()
    debug_enabled: bool = env_debug in {"1", "true", "yes", "on"}
    print("Validacao N2+N3 iniciada.", flush=True)

    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset: Dict[str, Any] = json.load(file)

    n2_model_data = _prepare_model_data_n2(dataset, predicts_dir, debug_enabled)
    n3_model_data = _prepare_model_data_n3(dataset, predicts_dir, debug_enabled)
    _compute_scores([n2_model_data, n3_model_data], debug_enabled)

    n2_metrics = _build_metrics(n2_model_data)
    n3_metrics = _build_metrics(n3_model_data)

    combined_models: Dict[str, Any] = {}
    combined_averages: Dict[str, Any] = {}
    n2_models: Dict[str, Any] = n2_metrics.get("models", {})
    n3_models: Dict[str, Any] = n3_metrics.get("models", {})

    for model in sorted(set(n2_models.keys()) | set(n3_models.keys())):
        n2_items = n2_models.get(model, {}).get("items", [])
        n3_items = n3_models.get(model, {}).get("items", [])
        merged_items = n2_items + n3_items

        averages: Dict[str, float | None] = {}
        for metric_name in METRIC_NAMES:
            values = _collect_metric_values(merged_items, metric_name)
            averages[metric_name] = sum(values) / len(values) if values else None

        combined_models[model] = {
            "counts": len(merged_items),
            "items": merged_items,
        }
        combined_averages[model] = averages

    combined: Dict[str, Any] = {
        "n2": n2_metrics,
        "n3": n3_metrics,
        "n2_n3": {
            "models": combined_models,
            "averages": combined_averages,
        },
    }

    _write_metrics(output_n2, n2_metrics)
    _write_metrics(output_n3, n3_metrics)
    _write_metrics(output_path, combined)

    print(f"Resultado salvo em {output_path}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar N2 e N3 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n2_n3.json")
    parser.add_argument("--output-n2", default="metrics/validate_n2.json")
    parser.add_argument("--output-n3", default="metrics/validate_n3.json")
    args: argparse.Namespace = parser.parse_args()

    validate_n2_n3(
        args.dataset,
        args.predicts,
        args.output,
        output_n2=args.output_n2,
        output_n3=args.output_n3,
    )
