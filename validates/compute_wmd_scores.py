from typing import List

from gensim.models import KeyedVectors


def compute_wmd_scores(word_vectors: KeyedVectors, targets: List[str], predictions: List[str]) -> List[float]:
    scores: List[float] = []
    for target, predicted in zip(targets, predictions):
        target_tokens = target.lower().split()
        predicted_tokens = predicted.lower().split()
        scores.append(word_vectors.wmdistance(target_tokens, predicted_tokens))
    return scores
