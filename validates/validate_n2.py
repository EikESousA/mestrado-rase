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


def build_pairs_n2(
    dataset: Dict[str, Any],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    dataset_items: List[Dict[str, Any]] = dataset.get("datas", [])
    predicted_items: List[Dict[str, Any]] = predictions.get("datas", [])

    for text_index, item in enumerate(dataset_items):
        predicted_item: Dict[str, Any] = (
            predicted_items[text_index] if text_index < len(predicted_items) else {}
        )
        predicted_texts: List[Dict[str, Any]] = predicted_item.get("texts_n1", [])
        for sentence_index, target_n1 in enumerate(item.get("texts_n1", [])):
            target_ops: Dict[str, Any] = target_n1.get("operators_n2", {}) or {}
            predicted_ops: Dict[str, Any] = {}
            if sentence_index < len(predicted_texts):
                predicted_ops = predicted_texts[sentence_index].get("operators_n2", {}) or {}

            for operator_name, operator_data in target_ops.items():
                target_text = ""
                if isinstance(operator_data, dict):
                    target_text = operator_data.get("text_n2", "")
                predicted_text = ""
                predicted_data = predicted_ops.get(operator_name, {})
                if isinstance(predicted_data, dict):
                    predicted_text = predicted_data.get("text_n2", "")

                pairs.append(
                    {
                        "text_index": text_index,
                        "sentence_index": sentence_index,
                        "operator": operator_name,
                        "text": item.get("text", ""),
                        "text_n1": target_n1.get("text_n1", ""),
                        "target": target_text,
                        "predicted": predicted_text,
                    }
                )
    return pairs


def validate_n2(dataset_path: str, predicts_dir: str, output_path: str) -> None:
    env_debug: str = os.getenv("GENERATE_DEBUG", "").strip().lower()
    debug_enabled: bool = env_debug in {"1", "true", "yes", "on"}
    print("Validacao N2 iniciada.", flush=True)

    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset: Dict[str, Any] = json.load(file)

    metrics: Dict[str, Any] = {"models": {}, "averages": {}}

    models: List[str] = ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]
    metric_names: List[str] = [
        "fuzzywuzzy",
        "tfidf",
        "sbert",
        "multilingual",
        "wmd_ft",
        "wmd_nilc",
    ]
    model_data: Dict[str, Dict[str, Any]] = {}

    for model in models:
        input_path = Path(predicts_dir) / f"generate_n2_{model}.json"

        if not input_path.exists():
            if debug_enabled:
                print(f"Pulando {model}: arquivo nao encontrado.", flush=True)
            continue

        print(f"Carregando modelo {model}...", flush=True)
        with open(input_path, "r", encoding="utf-8") as file:
            predictions: Dict[str, Any] = json.load(file)

        pairs: List[Dict[str, Any]] = build_pairs_n2(dataset, predictions)
        if debug_enabled:
            print(f"Pares gerados ({model}): {len(pairs)}", flush=True)

        targets: List[str] = [p["target"] for p in pairs]
        predicted: List[str] = [p["predicted"] for p in pairs]

        model_data[model] = {
            "pairs": pairs,
            "targets": targets,
            "predicted": predicted,
            "scores": {name: [] for name in metric_names},
        }

    for metric_name in metric_names:
        if metric_name == "fuzzywuzzy":
            for model, data in model_data.items():
                scores = [
                    fuzz.partial_ratio(t, p) / 100.0
                    for t, p in zip(data["targets"], data["predicted"])
                ]
                data["scores"][metric_name] = scores
                print(f"Modelo {model}: FuzzyWuzzy validado.", flush=True)
            continue
        if metric_name == "tfidf":
            for model, data in model_data.items():
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
            for model, data in model_data.items():
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
            for model, data in model_data.items():
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
                for model, data in model_data.items():
                    scores = compute_wmd_scores(word_vectors_ft, data["targets"], data["predicted"])
                    data["scores"][metric_name] = scores
                    print(f"Modelo {model}: WMD_FT validado.", flush=True)
                del word_vectors_ft
                gc.collect()
            else:
                for model in model_data:
                    data = model_data[model]
                    data["scores"][metric_name] = [None] * len(data["targets"])
                    print(f"Modelo {model}: WMD_FT indisponivel.", flush=True)
            continue
        if metric_name == "wmd_nilc":
            word_vectors_nilc: KeyedVectors | None = load_nilc_model()
            if word_vectors_nilc is not None:
                for model, data in model_data.items():
                    scores = compute_wmd_scores(word_vectors_nilc, data["targets"], data["predicted"])
                    data["scores"][metric_name] = scores
                    print(f"Modelo {model}: WMD_NILC validado.", flush=True)
                del word_vectors_nilc
                gc.collect()
            else:
                print(
                    "Modelo NILC nao encontrado em models/cbow_s300.txt ou src/models/cbow_s300.txt.",
                    flush=True,
                )
                for model in model_data:
                    data = model_data[model]
                    data["scores"][metric_name] = [None] * len(data["targets"])
                    print(f"Modelo {model}: WMD_NILC indisponivel.", flush=True)
            continue

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
        for metric_name in metric_names:
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
        if debug_enabled:
            print(f"Modelo {model} concluido.", flush=True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    print(f"Resultado salvo em {output_path}", flush=True)
    if debug_enabled:
        print("Validacao N2 finalizada.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar N2 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n2.json")
    args: argparse.Namespace = parser.parse_args()

    validate_n2(args.dataset, args.predicts, args.output)
