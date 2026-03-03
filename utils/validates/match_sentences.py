from difflib import SequenceMatcher
from typing import List, Tuple


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _similarity(left: str, right: str) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return SequenceMatcher(None, _normalize(left), _normalize(right)).ratio()


def align_sentence_indices(
    targets: List[str],
    predicted: List[str],
) -> List[Tuple[int | None, int | None, float]]:
    candidate_pairs: List[Tuple[float, int, int]] = []
    for target_index, target_text in enumerate(targets):
        for predicted_index, predicted_text in enumerate(predicted):
            score = _similarity(target_text, predicted_text)
            candidate_pairs.append((score, target_index, predicted_index))

    candidate_pairs.sort(key=lambda item: (-item[0], item[1], item[2]))

    used_targets: set[int] = set()
    used_predicted: set[int] = set()
    aligned: List[Tuple[int | None, int | None, float]] = []

    for score, target_index, predicted_index in candidate_pairs:
        if target_index in used_targets or predicted_index in used_predicted:
            continue
        used_targets.add(target_index)
        used_predicted.add(predicted_index)
        aligned.append((target_index, predicted_index, score))

    for target_index in range(len(targets)):
        if target_index not in used_targets:
            aligned.append((target_index, None, 0.0))

    for predicted_index in range(len(predicted)):
        if predicted_index not in used_predicted:
            aligned.append((None, predicted_index, 0.0))

    def _sort_key(item: Tuple[int | None, int | None, float]) -> Tuple[int, int]:
        target_index, predicted_index, _ = item
        if target_index is not None:
            return (target_index, predicted_index if predicted_index is not None else -1)
        return (10_000 + (predicted_index or 0), predicted_index if predicted_index is not None else -1)

    aligned.sort(key=_sort_key)
    return aligned
