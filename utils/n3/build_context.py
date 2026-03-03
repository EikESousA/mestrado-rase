def build_context(
    text_index: int,
    sentence_index: int | None = None,
    operator: str | None = None,
) -> str:
    parts = [f"text_index={text_index}"]
    if sentence_index is not None:
        parts.append(f"sentence_index={sentence_index}")
    if operator is not None:
        parts.append(f"operator={operator}")
    return "[" + " ".join(parts) + "]"
