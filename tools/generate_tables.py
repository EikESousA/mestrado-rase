"""Gera tabelas LaTeX e CSV a partir dos arquivos em metrics/.

Uso:
    python tools/generate_tables.py
    python tools/generate_tables.py --metrics-dir metrics --out-dir tables
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


METRIC_LABELS: Dict[str, str] = {
    "fuzzywuzzy": "FuzzyWuzzy",
    "tfidf": "TF-IDF",
    "sbert": "SBERT",
    "bertimbau": "BERTimbau",
    "multilingual": "Multilingual",
    "wmd_ft": "WMD-FT",
    "wmd_nilc": "WMD-NILC",
    "bertscore": "BERTScore",
    "rouge_l": "ROUGE-L",
}

CLASSIFICATION_KEYS = ("accuracy", "precision", "recall", "f1")


def _fmt(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return "-"


def _latex_table(
    title: str,
    label: str,
    columns: List[str],
    rows: List[List[str]],
) -> str:
    col_spec = "l" + "r" * (len(columns) - 1)
    lines: List[str] = [
        "\\begin{table}[ht]",
        "  \\centering",
        f"  \\caption{{{title}}}",
        f"  \\label{{{label}}}",
        f"  \\begin{{tabular}}{{{col_spec}}}",
        "    \\toprule",
        "    " + " & ".join(columns) + " \\\\",
        "    \\midrule",
    ]
    for row in rows:
        lines.append("    " + " & ".join(row) + " \\\\")
    lines.extend(["    \\bottomrule", "  \\end{tabular}", "\\end{table}"])
    return "\n".join(lines) + "\n"


def _similarity_rows(averages: Dict[str, Dict[str, Any]], metrics: Iterable[str]) -> List[List[str]]:
    rows: List[List[str]] = []
    for model in sorted(averages.keys()):
        row = [model] + [_fmt(averages[model].get(m)) for m in metrics]
        rows.append(row)
    return rows


def _classification_rows(averages: Dict[str, Dict[str, Any]]) -> List[List[str]]:
    rows: List[List[str]] = []
    for model in sorted(averages.keys()):
        macro = averages[model].get("classification_macro") or {}
        row = [model] + [_fmt(macro.get(k)) for k in CLASSIFICATION_KEYS]
        rows.append(row)
    return rows


def _build_tables_for_metrics(
    file_path: Path,
    out_dir: Path,
) -> None:
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Pulando {file_path}: {exc}")
        return

    level_key = file_path.stem.replace("validate_", "")
    averages: Dict[str, Dict[str, Any]] = {}
    if isinstance(data.get("averages"), dict):
        averages = data["averages"]
    elif isinstance(data.get(level_key), dict) and isinstance(data[level_key].get("averages"), dict):
        averages = data[level_key]["averages"]
    if not averages:
        print(f"Sem averages em {file_path}")
        return

    available_metrics = [m for m in METRIC_LABELS if any(
        m in v for v in averages.values()
    )]
    columns = ["Modelo"] + [METRIC_LABELS[m] for m in available_metrics]
    rows = _similarity_rows(averages, available_metrics)

    sim_tex = _latex_table(
        f"Metricas de similaridade ({level_key.upper()})",
        f"tab:results_{level_key}_similarity",
        columns,
        rows,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"results_{level_key}_similarity.tex").write_text(sim_tex)

    clf_rows = _classification_rows(averages)
    if any("-" != v for row in clf_rows for v in row[1:]):
        clf_tex = _latex_table(
            f"Metricas de classificacao ({level_key.upper()})",
            f"tab:results_{level_key}_classification",
            ["Modelo", "Accuracy", "Precision", "Recall", "F1"],
            clf_rows,
        )
        (out_dir / f"results_{level_key}_classification.tex").write_text(clf_tex)

    csv_path = out_dir / f"results_{level_key}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns + ["accuracy", "precision", "recall", "f1"])
        for sim_row, clf_row in zip(rows, clf_rows):
            writer.writerow(sim_row + clf_row[1:])


def generate_tables(
    levels: Optional[Sequence[str]] = None,
    metrics_dir: str = "metrics",
    out_dir: str = "tables",
) -> int:
    """Gera tabelas LaTeX/CSV a partir de metrics/validate_*.json.

    Retorna o numero de arquivos processados. Quando `levels` e informado,
    apenas os niveis listados (n1, n2, n3, n1n2, n1n2n3) sao processados.
    """
    metrics_path = Path(metrics_dir)
    out_path = Path(out_dir)

    if not metrics_path.is_dir():
        print(f"Diretorio nao encontrado: {metrics_path}")
        return 0

    all_files = sorted(metrics_path.glob("validate_*.json"))
    if levels:
        wanted = {f"validate_{lvl}.json" for lvl in levels}
        files = [f for f in all_files if f.name in wanted]
    else:
        files = all_files

    if not files:
        print(f"Nenhum arquivo correspondente em {metrics_path}")
        return 0

    for file_path in files:
        _build_tables_for_metrics(file_path, out_path)
        print(f"OK: {file_path.name}")
    print(f"Tabelas geradas em {out_path}/")
    return len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera tabelas LaTeX a partir de metrics/.")
    parser.add_argument("--metrics-dir", default="metrics")
    parser.add_argument("--out-dir", default="tables")
    parser.add_argument(
        "--levels",
        nargs="*",
        default=None,
        help="Niveis a processar (n1 n2 n3 n1n2 n1n2n3). Default: todos.",
    )
    args = parser.parse_args()
    generate_tables(levels=args.levels, metrics_dir=args.metrics_dir, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
