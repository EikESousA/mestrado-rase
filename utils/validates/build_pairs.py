from typing import Any, Dict, List

from utils.validates.match_sentences import align_sentence_indices


def build_pairs(
    dataset: Dict[str, Any],
    predictions: Dict[str, Any],
) -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    dataset_items: List[Dict[str, Any]] = dataset.get("datas", [])
    predicted_items: List[Dict[str, Any]] = predictions.get("datas", [])

    for text_index, item in enumerate(dataset_items):
        predicted_item: Dict[str, Any] = predicted_items[text_index] if text_index < len(predicted_items) else {}
        target_texts: List[Dict[str, Any]] = item.get("texts_n1", [])
        predicted_texts: List[Dict[str, Any]] = predicted_item.get("texts_n1", [])

        target_sentences = [target.get("text_n1", "") for target in target_texts]
        predicted_sentences = [pred.get("text_n1", "") for pred in predicted_texts]

        for target_index, predicted_index, alignment_score in align_sentence_indices(
            target_sentences,
            predicted_sentences,
        ):
            target_text = ""
            if target_index is not None and target_index < len(target_texts):
                target_text = target_texts[target_index].get("text_n1", "")

            predicted_text = ""
            if predicted_index is not None and predicted_index < len(predicted_texts):
                predicted_text = predicted_texts[predicted_index].get("text_n1", "")

            pairs.append(
                {
                    "text_index": text_index,
                    "sentence_index": target_index if target_index is not None else -1,
                    "predicted_sentence_index": predicted_index if predicted_index is not None else -1,
                    "alignment_score": alignment_score,
                    "text": item.get("text", ""),
                    "target": target_text,
                    "predicted": predicted_text,
                }
            )
    return pairs
