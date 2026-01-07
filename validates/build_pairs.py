from typing import Any, Dict, List


def build_pairs(
    dataset: Dict[str, Any],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    dataset_items = dataset.get("datas", [])
    predicted_items = predictions.get("datas", [])

    for text_index, item in enumerate(dataset_items):
        predicted_item = predicted_items[text_index] if text_index < len(predicted_items) else {}
        predicted_texts = predicted_item.get("texts_n1", [])
        for sentence_index, target in enumerate(item.get("texts_n1", [])):
            predicted_text = ""
            if sentence_index < len(predicted_texts):
                predicted_text = predicted_texts[sentence_index].get("text_n1", "")
            pairs.append(
                {
                    "text_index": text_index,
                    "sentence_index": sentence_index,
                    "text": item.get("text", ""),
                    "target": target.get("text_n1", ""),
                    "predicted": predicted_text,
                }
            )
    return pairs
