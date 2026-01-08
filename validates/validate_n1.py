import argparse
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List

import gensim.downloader as api
from fuzzywuzzy import fuzz
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

from utils.validates.build_pairs import build_pairs
from utils.validates.compute_sbert_scores import compute_sbert_scores
from utils.validates.compute_tfidf_scores import compute_tfidf_scores
from utils.validates.compute_wmd_scores import compute_wmd_scores
from utils.validates.load_nilc_model import load_nilc_model


def validate_n1(dataset_path: str, predicts_dir: str, output_path: str) -> None:
    env_debug: str = os.getenv("GENERATE_DEBUG", "").strip().lower()
    debug_enabled: bool = env_debug in {"1", "true", "yes", "on"}
    if debug_enabled:
        print("Validacao N1 iniciada.")
    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset: Dict[str, Any] = json.load(file)

    metrics: Dict[str, Any] = {"models": {}, "averages": {}}

    if debug_enabled:
        print("Carregando modelo SBERT...")
    sbert_model: SentenceTransformer = SentenceTransformer("tgsc/sentence-transformer-ult5-pt-small")

    word_vectors_ft: KeyedVectors | None = None
    try:
        if debug_enabled:
            print("Carregando modelo WMD_FT...")
        word_vectors_ft = api.load("fasttext-wiki-news-subwords-300")
    except Exception as exc:
        print(f"Falha ao carregar WMD_FT: {exc}")

    word_vectors_nilc: KeyedVectors | None = load_nilc_model()
    if word_vectors_nilc is None:
        print("Modelo NILC nao encontrado em models/cbow_s300.txt ou src/models/cbow_s300.txt.")

    models: List[str] = ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]
    for model in models:
        input_path = Path(predicts_dir) / f"generate_n1_{model}.json"
        if not input_path.exists():
            if debug_enabled:
                print(f"Pulando {model}: arquivo nao encontrado.")
            continue

        if debug_enabled:
            print(f"Processando modelo {model}...")
        with open(input_path, "r", encoding="utf-8") as file:
            predictions: Dict[str, Any] = json.load(file)

        pairs: List[Dict[str, Any]] = build_pairs(dataset, predictions)
        if debug_enabled:
            print(f"Pares gerados: {len(pairs)}")
        targets: List[str] = [p["target"] for p in pairs]
        predicted: List[str] = [p["predicted"] for p in pairs]

        fuzzy_scores: List[float] = [fuzz.partial_ratio(t, p) / 100.0 for t, p in zip(targets, predicted)]
        tfidf_scores: List[float] = compute_tfidf_scores(targets, predicted)
        sbert_scores: List[float] = compute_sbert_scores(sbert_model, targets, predicted)

        wmd_ft_scores: List[float] | None = None
        if word_vectors_ft is not None:
            wmd_ft_scores = compute_wmd_scores(word_vectors_ft, targets, predicted)

        wmd_nilc_scores: List[float] | None = None
        if word_vectors_nilc is not None:
            wmd_nilc_scores = compute_wmd_scores(word_vectors_nilc, targets, predicted)

        items: List[Dict[str, Any]] = []
        for i, pair in enumerate(pairs):
            items.append(
                {
                    **pair,
                    "fuzzywuzzy": fuzzy_scores[i] if i < len(fuzzy_scores) else None,
                    "tfidf": tfidf_scores[i] if i < len(tfidf_scores) else None,
                    "sbert": sbert_scores[i] if i < len(sbert_scores) else None,
                    "wmd_ft": wmd_ft_scores[i] if wmd_ft_scores is not None else None,
                    "wmd_nilc": wmd_nilc_scores[i] if wmd_nilc_scores is not None else None,
                }
            )

        averages: Dict[str, float | None] = {}
        for metric_name in ["fuzzywuzzy", "tfidf", "sbert", "wmd_ft", "wmd_nilc"]:
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
            print(f"Modelo {model} concluido.")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    print(f"Resultado salvo em {output_path}")
    if debug_enabled:
        print("Validacao N1 finalizada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar N1 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n1.json")
    args: argparse.Namespace = parser.parse_args()

    validate_n1(args.dataset, args.predicts, args.output)
