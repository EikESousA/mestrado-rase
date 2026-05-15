from typing import Any, Dict, List


def build_pairs_n2(
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
        predicted_texts: List[Dict[str, Any]] = predicted_item.get("texts_n1", [])
        for sentence_index, target_n1 in enumerate(item.get("texts_n1", [])):
            target_ops: Dict[str, Any] = target_n1.get("operators_n2", {}) or {}
            predicted_ops: Dict[str, Any] = {}
            if sentence_index < len(predicted_texts):
                predicted_ops = predicted_texts[sentence_index].get("operators_n2", {}) or {}

            for operator_name, operator_data in target_ops.items():
                target_text = ""
                if isinstance(operator_data, dict):
                    target_text = operator_data.get("text_n2", "")
                predicted_text = ""
                predicted_data = predicted_ops.get(operator_name, {})
                if isinstance(predicted_data, dict):
                    predicted_text = predicted_data.get("text_n2", "")

                pairs.append(
                    {
                        "text_index": text_index,
                        "sentence_index": sentence_index,
                        "operator": operator_name,
                        "text": item.get("text", ""),
                        "text_n1": target_n1.get("text_n1", ""),
                        "target": target_text,
                        "predicted": predicted_text,
                    }
                )
    return pairs
