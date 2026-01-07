import re
from typing import List


def split_sentences(text: str) -> List[str]:
    lines: List[str] = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [text.strip()]

    sentences: List[str] = []
    for line in lines:
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*\d+[\).\s-]+\s*", "", line)
        if not line:
            continue
        parts: List[str] = re.split(r"(?<!\b[A-Z])\.\s+(?![a-z])", line)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if not part.endswith("."):
                part += "."
            sentences.append(part)

    deduped: List[str] = []
    seen: set[str] = set()
    for sentence in sentences:
        if sentence not in seen:
            deduped.append(sentence)
            seen.add(sentence)

    return deduped
