import os


def is_debug_enabled() -> bool:
    env_debug = os.getenv("GENERATE_DEBUG", "").strip().lower()
    return env_debug in {"1", "true", "yes", "on"}
