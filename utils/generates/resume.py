import json
import os
from pathlib import Path
from typing import Any, Dict, List


def _resume_enabled() -> bool:
    """Default ligado; setar GEN_RESUME=0 desativa (forca refazer do zero)."""
    raw = os.environ.get("GEN_RESUME", "1").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def load_existing_output(output_path: str | Path) -> Dict[str, Any] | None:
    if not _resume_enabled():
        return None
    path = Path(output_path)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or "datas" not in data:
        return None
    return data


def already_processed(existing: Dict[str, Any] | None) -> int:
    if not existing:
        return 0
    datas = existing.get("datas")
    if not isinstance(datas, list):
        return 0
    return len(datas)


def checkpoint_path(output_path: str | Path) -> Path:
    return Path(str(output_path) + ".checkpoint.jsonl")


def append_checkpoint(output_path: str | Path, entry: Dict[str, Any]) -> None:
    path = checkpoint_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def consume_checkpoint(output_path: str | Path) -> List[Dict[str, Any]]:
    path = checkpoint_path(output_path)
    if not path.exists():
        return []
    items: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


def clear_checkpoint(output_path: str | Path) -> None:
    path = checkpoint_path(output_path)
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass
