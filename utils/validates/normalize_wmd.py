from typing import List


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
