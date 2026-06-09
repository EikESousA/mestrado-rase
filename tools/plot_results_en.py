"""Generates the English versions of the comparative bar charts for the article (artigo/figs)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_DIR = PROJECT_ROOT / "metrics"
OUT_DIR = PROJECT_ROOT / "artigo" / "figs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ORDER = ["dolphin", "llama", "mistral", "gemma", "alpaca", "qwen"]
MODEL_LABELS = {
    "dolphin": "Dolphin",
    "llama": "Llama",
    "mistral": "Mistral",
    "gemma": "Gemma",
    "alpaca": "Alpaca",
    "qwen": "Qwen",
}

SIMILARITY_METRICS = [
    "fuzzywuzzy",
    "tfidf",
    "sbert",
    "bertimbau",
    "multilingual",
    "wmd_ft",
    "wmd_nilc",
    "bertscore",
    "rouge_l",
]
METRIC_LABELS = {
    "fuzzywuzzy": "FuzzyWuzzy",
    "tfidf": "TF-IDF",
    "sbert": "SBERT",
    "bertimbau": "BERTimbau",
    "multilingual": "Multilingual",
    "wmd_ft": "WMD_ft",
    "wmd_nilc": "WMD_nilc",
    "bertscore": "BERTScore",
    "rouge_l": "ROUGE-L",
}


def load_averages(path: Path, sub_key: str | None = None) -> dict[str, dict[str, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    block = data[sub_key] if sub_key else data
    return block["averages"]


def matrix(averages: dict[str, dict[str, float]]) -> np.ndarray:
    rows = []
    for model in MODEL_ORDER:
        row = []
        for metric in SIMILARITY_METRICS:
            row.append(float(averages[model][metric]))
        rows.append(row)
    return np.array(rows)


def bar_plot(matrix_data: np.ndarray, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    n_models, n_metrics = matrix_data.shape
    x = np.arange(n_metrics)
    width = 0.8 / n_models
    cmap = plt.get_cmap("tab10")
    for i, model in enumerate(MODEL_ORDER):
        offset = (i - (n_models - 1) / 2) * width
        ax.bar(
            x + offset,
            matrix_data[i],
            width=width,
            label=MODEL_LABELS[model],
            color=cmap(i),
        )
    ax.set_xticks(x)
    ax.set_xticklabels([METRIC_LABELS[m] for m in SIMILARITY_METRICS], rotation=25, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title(title)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    n1 = matrix(load_averages(METRICS_DIR / "validate_n1.json"))
    n2 = matrix(load_averages(METRICS_DIR / "validate_n2.json"))
    n1n2 = matrix(load_averages(METRICS_DIR / "validate_n1n2.json", sub_key="n1n2"))

    bar_plot(n1, "Model $\\times$ metric comparison in EN1", OUT_DIR / "4.2.1-resultados-en1-barras-en.png")
    bar_plot(n2, "Model $\\times$ metric comparison in EN2", OUT_DIR / "4.2.2-resultados-en2-barras-en.png")
    bar_plot(n1n2, "Model $\\times$ metric comparison in EN1N2", OUT_DIR / "4.2.3-resultados-en1n2-barras-en.png")

    print("Generated in", OUT_DIR)


if __name__ == "__main__":
    main()
