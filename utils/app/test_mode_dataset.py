import json
from pathlib import Path
from typing import Any, Dict, List


def ensure_test_dataset(
    dataset_path: str = "dataset.json",
    output_path: str = "predicts/dataset_test.json",
    limit: int = 5,
) -> str:
    source_path = Path(dataset_path)
    target_path = Path(output_path)

    with source_path.open("r", encoding="utf-8") as file:
        dataset: Dict[str, Any] = json.load(file)

    items: List[Dict[str, Any]] = dataset.get("datas", [])
    sliced_items = items[: max(0, limit)]

    test_dataset: Dict[str, Any] = {
        "counts": len(sliced_items),
        "datas": sliced_items,
    }

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as file:
        json.dump(test_dataset, file, ensure_ascii=False, indent=2)

    return str(target_path)
