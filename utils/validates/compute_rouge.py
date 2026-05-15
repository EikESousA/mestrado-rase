from typing import List


def compute_rouge_l(
    targets: List[str],
    predictions: List[str],
) -> List[float | None]:
    if not targets:
        return []
    scores: List[float | None] = [None] * len(targets)
    try:
        from rouge_score.rouge_scorer import RougeScorer
    except ImportError:
        return scores
    scorer = RougeScorer(["rougeL"], use_stemmer=False)
    for i, (t, p) in enumerate(zip(targets, predictions)):
        if not (t.strip() and p.strip()):
            continue
        try:
            result = scorer.score(t, p)
            scores[i] = float(result["rougeL"].fmeasure)
        except Exception:
            continue
    return scores
