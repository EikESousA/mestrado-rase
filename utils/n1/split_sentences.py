import re
from typing import List

from utils.n1.normalize_sentence import normalize_sentence


SENTENCE_SPLIT_PATTERN = re.compile(r"(?<!\d)\.\s+(?=[A-ZÀ-Ý\"'])")


def _prepare_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(
        r"(?<=[.!?])\s+(?=\d+[\).]\s+[A-ZÀ-Ý])",
        "\n",
        normalized,
    )


def split_sentences(text: str) -> List[str]:
    prepared = _prepare_text(text)
    lines: List[str] = [line.strip() for line in prepared.splitlines() if line.strip()]
    if not lines:
        lines = [prepared.strip()]

    sentences: List[str] = []
    for line in lines:
        parts: List[str] = SENTENCE_SPLIT_PATTERN.split(line)
        for part in parts:
            part = normalize_sentence(part)
            if not part:
                continue
            if not re.search(r"[.!?]$", part):
                part += "."
            sentences.append(part)

    deduped: List[str] = []
    seen: set[str] = set()
    for sentence in sentences:
        if sentence not in seen:
            deduped.append(sentence)
            seen.add(sentence)

    return deduped
