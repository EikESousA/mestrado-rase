from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_tfidf_scores(targets: List[str], predictions: List[str]) -> List[float]:
    if not targets:
        return []
    vectorizer: TfidfVectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(targets + predictions)
    scores: List[float] = []
    for i in range(len(targets)):
        scores.append(cosine_similarity(tfidf_matrix[i], tfidf_matrix[i + len(targets)])[0][0])
    return scores
