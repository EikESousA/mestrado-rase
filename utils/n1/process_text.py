import re
from typing import List

from utils.n1.clean_output import clean_output
from utils.n1.split_sentences import split_sentences


def process_text(text: str) -> List[str]:
    cleaned: str = clean_output(text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return split_sentences(cleaned)
