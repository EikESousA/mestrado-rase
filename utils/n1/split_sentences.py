import re
from typing import List


_NLTK_TOKENIZER = None
_NLTK_FAILED = False


def _get_nltk_tokenizer():
    global _NLTK_TOKENIZER, _NLTK_FAILED
    if _NLTK_TOKENIZER is not None or _NLTK_FAILED:
        return _NLTK_TOKENIZER
    try:
        import nltk
        from nltk.tokenize import sent_tokenize as _sent_tokenize

        for resource in ("tokenizers/punkt_tab", "tokenizers/punkt"):
            try:
                nltk.data.find(resource)
                break
            except LookupError:
                try:
                    nltk.download(resource.split("/")[-1], quiet=True)
                except Exception:
                    continue
        _NLTK_TOKENIZER = _sent_tokenize
    except Exception:
        _NLTK_FAILED = True
        _NLTK_TOKENIZER = None
    return _NLTK_TOKENIZER


def _regex_split(line: str) -> List[str]:
    return re.split(r"(?<!\b[A-Z])\.\s+(?![a-z])", line)


def split_sentences(text: str) -> List[str]:
    lines: List[str] = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [text.strip()]

    tokenizer = _get_nltk_tokenizer()

    sentences: List[str] = []
    for line in lines:
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*\d+[\).\s-]+\s*", "", line)
        if not line:
            continue
        if tokenizer is not None:
            try:
                parts = tokenizer(line, language="portuguese")
            except Exception:
                parts = _regex_split(line)
        else:
            parts = _regex_split(line)
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
