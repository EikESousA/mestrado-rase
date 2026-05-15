import hashlib
import os
import subprocess
from typing import Any, Dict


def _prompt_sha256(prompt_text: str | None) -> str | None:
    if not prompt_text:
        return None
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()


def _git_sha() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(__file__),
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).decode().strip()
        return out or None
    except Exception:
        return None


def build_meta(
    model_id: str,
    prompt_text: str | None = None,
    seed: int | None = None,
    temperature: float = 0.1,
    top_p: float = 0.9,
    repeat_penalty: float = 1.1,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "model_id": model_id,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
    }
    if seed is not None:
        meta["seed"] = seed
    prompt_hash = _prompt_sha256(prompt_text)
    if prompt_hash:
        meta["prompt_sha256"] = prompt_hash
    git_sha = _git_sha()
    if git_sha:
        meta["code_git_sha"] = git_sha
    if extra:
        meta.update(extra)
    return meta


def env_seed() -> int | None:
    """Default 42 para reprodutibilidade. Setar GEN_SEED=none/off/'' desativa."""
    raw = os.environ.get("GEN_SEED", "42").strip()
    if raw.lower() in {"", "none", "off", "no", "0"}:
        return None
    try:
        return int(raw)
    except ValueError:
        return None
