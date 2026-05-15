from typing import Callable

from utils.generates.unload_model import unload_model


def reset_model(model_id: str, log: Callable[[str], None] | None = None) -> None:
    unload_model(model_id, log)
