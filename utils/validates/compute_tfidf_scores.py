from typing import Iterable, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def fit_tfidf_vectorizer(corpus: Iterable[str]) -> TfidfVectorizer:
    """Treina um TF-IDF uma vez sobre um corpus de referencia."""
    vectorizer = TfidfVectorizer()
    cleaned = [t for t in corpus if isinstance(t, str) and t.strip()]
    if not cleaned:
        cleaned = [""]
    vectorizer.fit(cleaned)
    return vectorizer


def compute_tfidf_scores(
    targets: List[str],
    predictions: List[str],
    vectorizer: TfidfVectorizer | None = None,
) -> List[float | None]:
    if not targets:
        return []
    scores: List[float | None] = [None] * len(targets)
    valid_indices = [
        i
        for i, (target, predicted) in enumerate(zip(targets, predictions))
        if target.strip() and predicted.strip()
    ]
    if not valid_indices:
        return scores
    valid_targets = [targets[i] for i in valid_indices]
    valid_predictions = [predictions[i] for i in valid_indices]

    if vectorizer is None:
        # Comportamento legado: vetorizador ad-hoc por chamada.
        vec = TfidfVectorizer()
        tfidf_matrix = vec.fit_transform(valid_targets + valid_predictions)
        n = len(valid_targets)
        target_matrix = tfidf_matrix[:n]
        predicted_matrix = tfidf_matrix[n:]
    else:
        target_matrix = vectorizer.transform(valid_targets)
        predicted_matrix = vectorizer.transform(valid_predictions)

    diag = cosine_similarity(target_matrix, predicted_matrix).diagonal()
    for local_index, original_index in enumerate(valid_indices):
        scores[original_index] = float(diag[local_index])
    return scores
