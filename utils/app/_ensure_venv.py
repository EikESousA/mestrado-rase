import subprocess
import sys
from pathlib import Path

from utils.app._requirements_hash import _requirements_hash


def _ensure_venv() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    venv_dir = root / ".venv"
    python_bin = venv_dir / "bin" / "python"
    req_file = root / "requirements.txt"
    stamp_file = venv_dir / ".requirements.sha256"

    if not venv_dir.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

    if req_file.exists():
        current_hash = _requirements_hash(req_file)
        previous_hash = stamp_file.read_text().strip() if stamp_file.exists() else ""
        if current_hash != previous_hash:
            subprocess.check_call(
                [str(python_bin), "-m", "pip", "install", "-r", str(req_file)]
            )
            stamp_file.write_text(current_hash + "\n")

    return python_bin
