from typing import List

import torch
from sentence_transformers import SentenceTransformer


def compute_sbert_scores(
    model: SentenceTransformer,
    targets: List[str],
    predictions: List[str],
    batch_size: int = 64,
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

    target_embeddings = model.encode(
        valid_targets,
        convert_to_tensor=True,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=False,
    )
    predicted_embeddings = model.encode(
        valid_predictions,
        convert_to_tensor=True,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=False,
    )
    diag = torch.sum(target_embeddings * predicted_embeddings, dim=1).tolist()
    for local_index, original_index in enumerate(valid_indices):
        scores[original_index] = float(diag[local_index])
    return scores
