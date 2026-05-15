"""Baseline nao-LLM (regex/heuristico) para N1, N2 e N3.

Gera arquivos no mesmo formato de `predicts/generate_<n>_<modelo>.json` com
modelo nominal `regex`. Usar como referencia inferior para ganhar interpretacao
dos numeros dos LLMs.

Uso:
    python tools/baseline_regex.py --level n1 --output predicts/generate_n1_regex.json
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.generates.meta import build_meta
from utils.n1.empty_operators import empty_operators
from utils.n1.split_sentences import split_sentences
from utils.n2.empty_properties import empty_properties


_REQ_PATTERNS = re.compile(
    r"\b(deve|devem|devera|deverao|devera-se|necessita|necessitam|sera|serao)\b",
    flags=re.IGNORECASE,
)
_APP_PATTERNS = re.compile(
    r"^\s*(em|nas?|nos?|para|quando|aos?|as?|os?)\b", flags=re.IGNORECASE
)
_EXC_PATTERNS = re.compile(
    r"\b(exceto|salvo|excluindo|com\s+excecao|exceto\s+quando)\b",
    flags=re.IGNORECASE,
)
_SEL_PATTERNS = re.compile(
    r"\b(quando|caso|se|desde\s+que|sempre\s+que)\b", flags=re.IGNORECASE
)
_NUM_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*(m|cm|mm|kg|h|min|s|%)?", flags=re.IGNORECASE)


def _baseline_n2(text_n1: str) -> Dict[str, Dict[str, Any]]:
    ops: Dict[str, Dict[str, Any]] = {
        "aplicability": {"text_n2": "", "properties_n3": empty_properties()},
        "selection": {"text_n2": "", "properties_n3": empty_properties()},
        "exception": {"text_n2": "", "properties_n3": empty_properties()},
        "requeriments": {"text_n2": "", "properties_n3": empty_properties()},
    }
    if _APP_PATTERNS.search(text_n1):
        m = _APP_PATTERNS.search(text_n1)
        if m:
            ops["aplicability"]["text_n2"] = text_n1[m.start():].split(",")[0]
    if _SEL_PATTERNS.search(text_n1):
        m = _SEL_PATTERNS.search(text_n1)
        if m:
            ops["selection"]["text_n2"] = text_n1[m.start():].split(",")[0]
    if _EXC_PATTERNS.search(text_n1):
        m = _EXC_PATTERNS.search(text_n1)
        if m:
            ops["exception"]["text_n2"] = text_n1[m.start():].split(",")[0]
    if _REQ_PATTERNS.search(text_n1):
        m = _REQ_PATTERNS.search(text_n1)
        if m:
            ops["requeriments"]["text_n2"] = text_n1[m.start():]
    return ops


def _baseline_n3(text_n2: str, op_type: str) -> Dict[str, str]:
    if not text_n2.strip():
        return empty_properties()
    props = empty_properties()
    type_label = {"aplicability": "aplicabilidade", "selection": "selecao",
                  "exception": "excecao", "requeriments": "requisito"}[op_type]
    props["type"] = type_label
    nm = _NUM_PATTERN.search(text_n2)
    if nm:
        props["target"] = nm.group(1)
        if nm.group(2):
            props["unit"] = nm.group(2).lower()
    return props


def generate_n1(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in dataset.get("datas", []):
        sentences = split_sentences(item.get("text", ""))
        texts_n1 = [{"text_n1": s, "operators_n2": empty_operators()} for s in sentences]
        out.append({"text": item.get("text", ""), "texts_n1": texts_n1})
    return out


def generate_n2(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in dataset.get("datas", []):
        sentences = split_sentences(item.get("text", ""))
        texts_n1 = []
        for s in sentences:
            texts_n1.append({"text_n1": s, "operators_n2": _baseline_n2(s)})
        out.append({"text": item.get("text", ""), "texts_n1": texts_n1})
    return out


def generate_n3(dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in dataset.get("datas", []):
        sentences = split_sentences(item.get("text", ""))
        texts_n1 = []
        for s in sentences:
            ops = _baseline_n2(s)
            for op_key, op_payload in ops.items():
                op_payload["properties_n3"] = _baseline_n3(op_payload["text_n2"], op_key)
            texts_n1.append({"text_n1": s, "operators_n2": ops})
        out.append({"text": item.get("text", ""), "texts_n1": texts_n1})
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline regex para N1/N2/N3.")
    parser.add_argument("--level", choices=["n1", "n2", "n3"], required=True)
    parser.add_argument("--dataset", default="dataset.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    start = time.time()
    if args.level == "n1":
        datas = generate_n1(dataset)
    elif args.level == "n2":
        datas = generate_n2(dataset)
    else:
        datas = generate_n3(dataset)
    elapsed = time.time() - start

    result = {
        "meta": build_meta(model_id="regex-baseline", prompt_text=None, seed=None),
        "counts": len(datas),
        "datas": datas,
        "time": elapsed,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Baseline {args.level} gerado em {elapsed:.2f}s -> {args.output}")


if __name__ == "__main__":
    main()
