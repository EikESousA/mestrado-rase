import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import gensim.downloader as api
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer

from validates.build_pairs import build_pairs
from validates.compute_sbert_scores import compute_sbert_scores
from validates.compute_tfidf_scores import compute_tfidf_scores
from validates.compute_wmd_scores import compute_wmd_scores
from validates.load_nilc_model import load_nilc_model
from validates.normalize_wmd import normalize_wmd


def validate_n1(dataset_path: str, predicts_dir: str, output_path: str) -> None:
    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    metrics: Dict[str, Any] = {"models": {}}

    sbert_model = SentenceTransformer("tgsc/sentence-transformer-ult5-pt-small")

    word_vectors_ft = None
    try:
        word_vectors_ft = api.load("fasttext-wiki-news-subwords-300")
    except Exception as exc:
        print(f"Falha ao carregar WMD_FT: {exc}")

    word_vectors_nilc = load_nilc_model()
    if word_vectors_nilc is None:
        print("Modelo NILC nao encontrado em models/cbow_s300.txt ou src/models/cbow_s300.txt.")

    for model in ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]:
        input_path = Path(predicts_dir) / f"generate_n1_{model}.json"
        if not input_path.exists():
            continue

        with open(input_path, "r", encoding="utf-8") as file:
            predictions = json.load(file)

        pairs = build_pairs(dataset, predictions)
        targets = [p["target"] for p in pairs]
        predicted = [p["predicted"] for p in pairs]

        fuzzy_scores = [fuzz.partial_ratio(t, p) / 100.0 for t, p in zip(targets, predicted)]
        tfidf_scores = compute_tfidf_scores(targets, predicted)
        sbert_scores = compute_sbert_scores(sbert_model, targets, predicted)

        wmd_ft_scores: List[float] | None = None
        if word_vectors_ft is not None:
            wmd_ft_scores = normalize_wmd(compute_wmd_scores(word_vectors_ft, targets, predicted))

        wmd_nilc_scores: List[float] | None = None
        if word_vectors_nilc is not None:
            wmd_nilc_scores = normalize_wmd(compute_wmd_scores(word_vectors_nilc, targets, predicted))

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

        metrics["models"][model] = {"counts": len(items), "items": items}

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    print(f"Resultado salvo em {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar N1 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n1.json")
    args = parser.parse_args()

    validate_n1(args.dataset, args.predicts, args.output)
