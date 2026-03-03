from typing import Any, Dict, List


OPERATOR_ORDER: List[str] = ["aplicability", "selection", "exception", "requeriments"]


def _build_metrics(tp: int, fp: int, fn: int, tn: int) -> Dict[str, float | int]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "support": tp + fn,
        "predicted_positive": tp + fp,
    }


def _presence_from_text(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return bool(value.strip())


def _presence_from_properties(properties: Any) -> bool:
    if not isinstance(properties, dict):
        return False
    for key in ("type", "object", "property", "comparation", "target", "unit"):
        value = properties.get(key, "")
        if isinstance(value, str) and value.strip():
            return True
    return False


def _aggregate_macro(operator_report: Dict[str, Dict[str, float | int]]) -> Dict[str, float]:
    if not operator_report:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    precisions = [float(values["precision"]) for values in operator_report.values()]
    recalls = [float(values["recall"]) for values in operator_report.values()]
    f1s = [float(values["f1"]) for values in operator_report.values()]
    total = len(operator_report)
    return {
        "precision": sum(precisions) / total,
        "recall": sum(recalls) / total,
        "f1": sum(f1s) / total,
    }


def _aggregate_micro(operator_report: Dict[str, Dict[str, float | int]]) -> Dict[str, float]:
    tp = sum(int(values["tp"]) for values in operator_report.values())
    fp = sum(int(values["fp"]) for values in operator_report.values())
    fn = sum(int(values["fn"]) for values in operator_report.values())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def compute_operator_report_n2(pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
    raw_counts: Dict[str, Dict[str, int]] = {
        operator: {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for operator in OPERATOR_ORDER
    }

    for pair in pairs:
        operator = pair.get("operator", "")
        if operator not in raw_counts:
            continue
        target_has = _presence_from_text(pair.get("target", ""))
        predicted_has = _presence_from_text(pair.get("predicted", ""))
        counts = raw_counts[operator]
        if target_has and predicted_has:
            counts["tp"] += 1
        elif (not target_has) and predicted_has:
            counts["fp"] += 1
        elif target_has and (not predicted_has):
            counts["fn"] += 1
        else:
            counts["tn"] += 1

    by_operator = {
        operator: _build_metrics(
            values["tp"],
            values["fp"],
            values["fn"],
            values["tn"],
        )
        for operator, values in raw_counts.items()
    }
    return {
        "by_operator": by_operator,
        "macro_avg": _aggregate_macro(by_operator),
        "micro_avg": _aggregate_micro(by_operator),
    }


def compute_operator_report_n3(pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
    raw_counts: Dict[str, Dict[str, int]] = {
        operator: {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for operator in OPERATOR_ORDER
    }

    for pair in pairs:
        operator = pair.get("operator", "")
        if operator not in raw_counts:
            continue
        target_has = _presence_from_properties(pair.get("target_properties"))
        predicted_has = _presence_from_properties(pair.get("predicted_properties"))
        counts = raw_counts[operator]
        if target_has and predicted_has:
            counts["tp"] += 1
        elif (not target_has) and predicted_has:
            counts["fp"] += 1
        elif target_has and (not predicted_has):
            counts["fn"] += 1
        else:
            counts["tn"] += 1

    by_operator = {
        operator: _build_metrics(
            values["tp"],
            values["fp"],
            values["fn"],
            values["tn"],
        )
        for operator, values in raw_counts.items()
    }
    return {
        "by_operator": by_operator,
        "macro_avg": _aggregate_macro(by_operator),
        "micro_avg": _aggregate_micro(by_operator),
    }
