def normalize_value(value: str) -> str:
    normalized = value.strip().strip('"').strip("'").strip()
    if normalized.lower() in {"", "null", "none", '""', "''", "n/a"}:
        return ""
    return normalized
