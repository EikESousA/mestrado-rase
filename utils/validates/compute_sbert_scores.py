from typing import List

from sentence_transformers import SentenceTransformer, util


def compute_sbert_scores(
    model: SentenceTransformer,
    targets: List[str],
    predictions: List[str],
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
    target_embeddings = model.encode(valid_targets, convert_to_tensor=True)
    predicted_embeddings = model.encode(valid_predictions, convert_to_tensor=True)
    for local_index, original_index in enumerate(valid_indices):
        scores[original_index] = util.pytorch_cos_sim(
            target_embeddings[local_index],
            predicted_embeddings[local_index],
        ).item()
    return scores
