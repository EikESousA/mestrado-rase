from typing import List


def compute_bertscore(
    targets: List[str],
    predictions: List[str],
    lang: str = "pt",
    model_type: str | None = None,
) -> List[float | None]:
    if not targets:
        return []
    scores: List[float | None] = [None] * len(targets)
    valid_indices = [
        i
        for i, (t, p) in enumerate(zip(targets, predictions))
        if t.strip() and p.strip()
    ]
    if not valid_indices:
        return scores
    try:
        from bert_score import score as bert_score
    except ImportError:
        return scores
    valid_targets = [targets[i] for i in valid_indices]
    valid_predictions = [predictions[i] for i in valid_indices]
    kwargs = {"lang": lang, "verbose": False, "rescale_with_baseline": False}
    if model_type:
        kwargs["model_type"] = model_type
    try:
        _, _, f1 = bert_score(valid_predictions, valid_targets, **kwargs)
    except Exception as exc:
        print(f"BERTScore falhou: {exc}")
        return scores
    f1_list = f1.tolist()
    for local_index, original_index in enumerate(valid_indices):
        scores[original_index] = float(f1_list[local_index])
    return scores
