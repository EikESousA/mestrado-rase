import re
from typing import Any, Dict, List


def empty_operators() -> Dict[str, str]:
    return {
        "requeriments": "",
        "aplicability": "",
        "selection": "",
        "exception": "",
    }


def clean_output(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"(?i)^(resposta|saida)\s*:\s*", "", cleaned)
    cleaned = cleaned.strip().strip('"').strip("'").strip()
    return cleaned


def split_sentences(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [text.strip()]

    sentences: List[str] = []
    for line in lines:
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*\d+[\).\s-]+\s*", "", line)
        if not line:
            continue
        parts = re.split(r"(?<!\b[A-Z])\.\s+(?![a-z])", line)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if not part.endswith("."):
                part += "."
            sentences.append(part)

    deduped: List[str] = []
    seen = set()
    for sentence in sentences:
        if sentence not in seen:
            deduped.append(sentence)
            seen.add(sentence)

    return deduped


def process_text(text: str) -> List[str]:
    cleaned = clean_output(text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return split_sentences(cleaned)
