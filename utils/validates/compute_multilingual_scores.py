from typing import List

from sentence_transformers import SentenceTransformer, util


def compute_multilingual_scores(
    model: SentenceTransformer,
    targets: List[str],
    predictions: List[str],
) -> List[float]:
    if not targets:
        return []
    target_embeddings = model.encode(targets, convert_to_tensor=True)
    predicted_embeddings = model.encode(predictions, convert_to_tensor=True)
    scores: List[float] = []
    for i in range(len(targets)):
        scores.append(util.pytorch_cos_sim(target_embeddings[i], predicted_embeddings[i]).item())
    return scores
