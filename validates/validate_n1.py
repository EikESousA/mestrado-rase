import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fuzzywuzzy import fuzz
from gensim.models import KeyedVectors
import gensim.downloader as api
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODELS = ["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]


def build_pairs(
    dataset: Dict[str, Any],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    dataset_items = dataset.get("datas", [])
    predicted_items = predictions.get("datas", [])

    for text_index, item in enumerate(dataset_items):
        predicted_item = predicted_items[text_index] if text_index < len(predicted_items) else {}
        predicted_texts = predicted_item.get("texts_n1", [])
        for sentence_index, target in enumerate(item.get("texts_n1", [])):
            predicted_text = ""
            if sentence_index < len(predicted_texts):
                predicted_text = predicted_texts[sentence_index].get("text_n1", "")
            pairs.append(
                {
                    "text_index": text_index,
                    "sentence_index": sentence_index,
                    "text": item.get("text", ""),
                    "target": target.get("text_n1", ""),
                    "predicted": predicted_text,
                }
            )
    return pairs


def normalize_wmd(scores: List[float]) -> List[float]:
    if not scores:
        return []
    finite_scores = [s for s in scores if s != float("inf")]
    if not finite_scores:
        return [0.0 for _ in scores]
    min_score = min(finite_scores)
    max_score = max(finite_scores)
    if max_score == min_score:
        return [1.0 if s != float("inf") else 0.0 for s in scores]
    normalized: List[float] = []
    for s in scores:
        if s == float("inf"):
            normalized.append(0.0)
        else:
            normalized.append(1 - ((s - min_score) / (max_score - min_score)))
    return normalized


def compute_tfidf_scores(targets: List[str], predictions: List[str]) -> List[float]:
    if not targets:
        return []
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(targets + predictions)
    scores: List[float] = []
    for i in range(len(targets)):
        scores.append(cosine_similarity(tfidf_matrix[i], tfidf_matrix[i + len(targets)])[0][0])
    return scores


def compute_sbert_scores(model: SentenceTransformer, targets: List[str], predictions: List[str]) -> List[float]:
    if not targets:
        return []
    target_embeddings = model.encode(targets, convert_to_tensor=True)
    predicted_embeddings = model.encode(predictions, convert_to_tensor=True)
    scores: List[float] = []
    for i in range(len(targets)):
        scores.append(util.pytorch_cos_sim(target_embeddings[i], predicted_embeddings[i]).item())
    return scores


def compute_wmd_scores(word_vectors: KeyedVectors, targets: List[str], predictions: List[str]) -> List[float]:
    scores: List[float] = []
    for target, predicted in zip(targets, predictions):
        target_tokens = target.lower().split()
        predicted_tokens = predicted.lower().split()
        scores.append(word_vectors.wmdistance(target_tokens, predicted_tokens))
    return scores


def load_nilc_model() -> KeyedVectors | None:
    candidates = [Path("models") / "cbow_s300.txt", Path("src") / "models" / "cbow_s300.txt"]
    for candidate in candidates:
        if candidate.exists():
            return KeyedVectors.load_word2vec_format(
                str(candidate),
                encoding="utf-8",
                unicode_errors="ignore",
            )
    return None


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

    for model in MODELS:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Validar N1 usando similaridades.")
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--predicts", default="predicts")
    parser.add_argument("--output", default="metrics/validate_n1.json")
    args = parser.parse_args()

    validate_n1(args.dataset, args.predicts, args.output)


if __name__ == "__main__":
    main()
