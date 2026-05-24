"""Gera gráficos comparativos a partir dos JSONs de validação."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_DIR = PROJECT_ROOT / "metrics"
OUT_DIR = PROJECT_ROOT / "dissertacao" / "Imagens"
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
    "wmd_ft": "WMD\\_ft",
    "wmd_nilc": "WMD\\_nilc",
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
    ax.set_xticklabels([METRIC_LABELS[m].replace("\\_", "_") for m in SIMILARITY_METRICS], rotation=25, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title(title)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def heatmap(matrix_data: np.ndarray, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    im = ax.imshow(matrix_data, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(SIMILARITY_METRICS)))
    ax.set_xticklabels(
        [METRIC_LABELS[m].replace("\\_", "_") for m in SIMILARITY_METRICS],
        rotation=25,
        ha="right",
    )
    ax.set_yticks(range(len(MODEL_ORDER)))
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODEL_ORDER])
    for i in range(matrix_data.shape[0]):
        for j in range(matrix_data.shape[1]):
            val = matrix_data[i, j]
            ax.text(
                j,
                i,
                f"{val:.2f}",
                ha="center",
                va="center",
                color="white" if val < 0.55 else "black",
                fontsize=8,
            )
    ax.set_title(title)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02, label="Score")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def heatmap_global(global_mat: np.ndarray, experiments: list[str], out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5, 4.5))
    im = ax.imshow(global_mat, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(experiments)))
    ax.set_xticklabels(experiments)
    ax.set_yticks(range(len(MODEL_ORDER)))
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODEL_ORDER])
    for i in range(global_mat.shape[0]):
        for j in range(global_mat.shape[1]):
            val = global_mat[i, j]
            ax.text(
                j,
                i,
                f"{val:.3f}",
                ha="center",
                va="center",
                color="white" if val < 0.55 else "black",
                fontsize=9,
            )
    ax.set_title("Média das 9 métricas de similaridade por modelo e experimento")
    fig.colorbar(im, ax=ax, fraction=0.05, pad=0.04, label="Score")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    n1 = matrix(load_averages(METRICS_DIR / "validate_n1.json"))
    n2 = matrix(load_averages(METRICS_DIR / "validate_n2.json"))
    n1n2 = matrix(load_averages(METRICS_DIR / "validate_n1n2.json", sub_key="n1n2"))

    bar_plot(n1, "EN1 — Segmentação N1: modelos × métricas", OUT_DIR / "4.2.1-resultados-en1-barras.png")
    bar_plot(n2, "EN2 — Identificação RASE: modelos × métricas", OUT_DIR / "4.2.2-resultados-en2-barras.png")
    bar_plot(n1n2, "EN1N2 — Pipeline encadeado: modelos × métricas", OUT_DIR / "4.2.3-resultados-en1n2-barras.png")

    print("Gerados em", OUT_DIR)


if __name__ == "__main__":
    main()
