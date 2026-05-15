from typing import Any, Dict, List

from utils.validates.align_pairs import align_lists


def build_pairs(
    dataset: Dict[str, Any],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    dataset_items: List[Dict[str, Any]] = dataset.get("datas", [])
    predicted_items: List[Dict[str, Any]] = predictions.get("datas", [])

    for text_index, item in enumerate(dataset_items):
        predicted_item: Dict[str, Any] = (
            predicted_items[text_index] if text_index < len(predicted_items) else {}
        )
        target_texts: List[Dict[str, Any]] = list(item.get("texts_n1", []))
        predicted_texts: List[Dict[str, Any]] = list(predicted_item.get("texts_n1", []))

        target_strs = [t.get("text_n1", "") for t in target_texts]
        predicted_strs = [p.get("text_n1", "") for p in predicted_texts]

        alignments = align_lists(target_strs, predicted_strs)

        sentence_counter = 0
        for ti, pi in alignments:
            if ti is None:
                # Predito sem alvo (FP em metricas de classificacao).
                pairs.append(
                    {
                        "text_index": text_index,
                        "sentence_index": sentence_counter,
                        "text": item.get("text", ""),
                        "target": "",
                        "predicted": predicted_strs[pi] if pi is not None else "",
                    }
                )
            else:
                pairs.append(
                    {
                        "text_index": text_index,
                        "sentence_index": ti,
                        "text": item.get("text", ""),
                        "target": target_strs[ti],
                        "predicted": predicted_strs[pi] if pi is not None else "",
                    }
                )
            sentence_counter += 1
    return pairs
