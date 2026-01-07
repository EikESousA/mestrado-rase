from pathlib import Path

from gensim.models import KeyedVectors


def load_nilc_model() -> KeyedVectors | None:
    candidates: list[Path] = [Path("models") / "cbow_s300.txt", Path("src") / "models" / "cbow_s300.txt"]
    for candidate in candidates:
        if candidate.exists():
            return KeyedVectors.load_word2vec_format(
                str(candidate),
                encoding="utf-8",
                unicode_errors="ignore",
            )
    return None
