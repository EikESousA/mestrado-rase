import re


LETTER_PATTERN = re.compile(r"[A-Za-zÀ-ÿ]")
ECHO_PREFIX_PATTERN = re.compile(
    r"^(?:entrada|texto(?:\s+completo|\s+n1|_inicio|_fim)?|input)\s*:\s*",
    re.IGNORECASE,
)
OUTPUT_PREFIX_PATTERN = re.compile(
    r"^(?:resposta|saida|saída|output)\s*:\s*",
    re.IGNORECASE,
)
NUMBERING_PREFIX_PATTERN = re.compile(r"^\s*(?:[-*]+|\d+[\).\s-]+)\s*")
NUMBERING_ONLY_PATTERN = re.compile(r"^\s*\d+[\).]?\s*$")


def normalize_sentence(text: str) -> str:
    normalized = " ".join(text.strip().split())
    if not normalized:
        return ""

    if ECHO_PREFIX_PATTERN.match(normalized):
        return ""

    normalized = OUTPUT_PREFIX_PATTERN.sub("", normalized)
    normalized = NUMBERING_PREFIX_PATTERN.sub("", normalized)
    normalized = normalized.strip().strip('"').strip("'").strip()

    if not normalized or NUMBERING_ONLY_PATTERN.match(normalized):
        return ""
    if not LETTER_PATTERN.search(normalized):
        return ""

    return normalized
