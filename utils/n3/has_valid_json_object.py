import json


def has_valid_json_object(text: str) -> bool:
    cleaned = text.strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return False
    snippet = cleaned[start : end + 1]
    try:
        parsed = json.loads(snippet)
    except json.JSONDecodeError:
        return False
    return isinstance(parsed, dict)
