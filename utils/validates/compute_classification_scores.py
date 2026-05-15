import unicodedata
from typing import Any, Dict, List, Tuple

THRESHOLD_DEFAULT: float = 0.7


def _normalize(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    return text.lower().strip().rstrip(".,;:")


def _safe_div(num: float, den: float) -> float:
    return num / den if den > 0 else 0.0


def compute_confusion_from_similarity(
    similarities: List[float | None],
    targets: List[str],
    predictions: List[str],
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict[str, int]:
    tp = fp = fn = tn = 0
    for sim, t, p in zip(similarities, targets, predictions):
        t_has = bool(t and t.strip())
        p_has = bool(p and p.strip())
        if t_has and p_has:
            if sim is not None and sim >= threshold:
                tp += 1
            else:
                fp += 1
                fn += 1
        elif t_has and not p_has:
            fn += 1
        elif p_has and not t_has:
            fp += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def compute_confusion_from_exact(
    target_props: List[Dict[str, Any]],
    predicted_props: List[Dict[str, Any]],
    fields: Tuple[str, ...] = ("object", "property", "comparation", "target", "unit"),
) -> Dict[str, Dict[str, int]]:
    per_field: Dict[str, Dict[str, int]] = {
        f: {"tp": 0, "fp": 0, "fn": 0, "tn": 0} for f in fields
    }
    for t_props, p_props in zip(target_props, predicted_props):
        for field in fields:
            t_val = _normalize(t_props.get(field, "") if isinstance(t_props, dict) else "")
            p_val = _normalize(p_props.get(field, "") if isinstance(p_props, dict) else "")
            if t_val and p_val:
                if t_val == p_val:
                    per_field[field]["tp"] += 1
                else:
                    per_field[field]["fp"] += 1
                    per_field[field]["fn"] += 1
            elif t_val and not p_val:
                per_field[field]["fn"] += 1
            elif p_val and not t_val:
                per_field[field]["fp"] += 1
            else:
                per_field[field]["tn"] += 1
    return per_field


def metrics_from_confusion(conf: Dict[str, int]) -> Dict[str, float]:
    tp, fp, fn, tn = conf["tp"], conf["fp"], conf["fn"], conf["tn"]
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    accuracy = _safe_div(tp + tn, tp + tn + fp + fn)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def macro_average(per_field_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    keys = ("accuracy", "precision", "recall", "f1")
    n = len(per_field_metrics)
    if n == 0:
        return {k: 0.0 for k in keys}
    return {k: sum(m[k] for m in per_field_metrics.values()) / n for k in keys}
