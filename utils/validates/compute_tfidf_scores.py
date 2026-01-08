from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_scores(targets: List[str], predictions: List[str]) -> List[float | None]:
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
    vectorizer: TfidfVectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(valid_targets + valid_predictions)
    for local_index, original_index in enumerate(valid_indices):
        scores[original_index] = cosine_similarity(
            tfidf_matrix[local_index],
            tfidf_matrix[local_index + len(valid_targets)],
        )[0][0]
    return scores
