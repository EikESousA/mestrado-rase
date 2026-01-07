import hashlib
from pathlib import Path


def _requirements_hash(req_path: Path) -> str:
    return hashlib.sha256(req_path.read_bytes()).hexdigest()
