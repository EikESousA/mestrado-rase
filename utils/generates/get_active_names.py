from typing import List


def get_active_names(options: List[tuple[str, bool]]) -> List[str]:
    return [name for name, active in options if active]
