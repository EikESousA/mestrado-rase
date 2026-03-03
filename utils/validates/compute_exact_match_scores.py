from typing import List


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def compute_exact_match_scores(targets: List[str], predicted: List[str]) -> List[float]:
    scores: List[float] = []
    for target, prediction in zip(targets, predicted):
        scores.append(1.0 if _normalize(target) == _normalize(prediction) else 0.0)
    return scores
