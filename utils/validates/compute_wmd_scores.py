import math
from typing import List

from gensim.models import KeyedVectors


def compute_wmd_scores(
    word_vectors: KeyedVectors,
    targets: List[str],
    predictions: List[str],
) -> List[float | None]:
    scores: List[float | None] = []
    for target, predicted in zip(targets, predictions):
        target_tokens = target.lower().split()
        predicted_tokens = predicted.lower().split()
        try:
            distance = word_vectors.wmdistance(target_tokens, predicted_tokens)
        except Exception:
            scores.append(None)
            continue
        if not math.isfinite(distance):
            scores.append(None)
            continue
        scores.append(distance)
    return scores
