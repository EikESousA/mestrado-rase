"""Generates the English version of the pipeline diagram for the article (figs/pipeline-en.png)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "artigo" / "figs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def box(ax, x, y, w, h, text, facecolor="#E8F0FE", edgecolor="#1A73E8", fontsize=10, weight="normal"):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.5,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, fontweight=weight)


def arrow(ax, x1, y1, x2, y2, label=None, color="#5F6368", style="->", curve=0.0, label_dy=0.18, label_fs=8):
    arr = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle=style,
        color=color,
        linewidth=1.6,
        mutation_scale=18,
        connectionstyle=f"arc3,rad={curve}",
    )
    ax.add_patch(arr)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(
            mx,
            my + label_dy,
            label,
            ha="center",
            va="bottom",
            fontsize=label_fs,
            color=color,
            style="italic",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none"),
        )


def plot_pipeline() -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Ollama container box (top)
    container = FancyBboxPatch(
        (2.7, 4.2),
        10.6,
        2.4,
        boxstyle="round,pad=0.05,rounding_size=0.08",
        facecolor="#F8F9FA",
        edgecolor="#9AA0A6",
        linewidth=1.2,
        linestyle="--",
    )
    ax.add_patch(container)
    ax.text(8.0, 6.35, "Ollama — 6 LLMs (Llama, Dolphin, Gemma, Mistral, Alpaca, Qwen)",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#5F6368")

    # Main line
    y_main = 5.2
    box(ax, 1.5, y_main, 2.0, 1.3, "dataset.json\n(79 standards)\nraw text", facecolor="#FFF3E0", edgecolor="#E8710A", fontsize=9)
    box(ax, 5.0, y_main, 2.3, 1.5, "N1: Atomic\nSegmentation\n(Prompt Direct)", facecolor="#E8F0FE", edgecolor="#1A73E8", fontsize=9)
    box(ax, 8.0, y_main, 2.3, 1.5, "N2: RASE\nOperators (R/A/S/E)\n(Chain-of-Thought)", facecolor="#E8F0FE", edgecolor="#1A73E8", fontsize=9)
    box(ax, 11.0, y_main, 2.3, 1.5, "N3: Structured\nJSON\n(Few-Shot)", facecolor="#E8F0FE", edgecolor="#1A73E8", fontsize=9)
    box(ax, 14.3, y_main, 1.8, 1.3, "Final RASE\nJSON", facecolor="#E6F4EA", edgecolor="#188038", fontsize=9, weight="bold")

    arrow(ax, 2.55, y_main, 3.8, y_main, label="text", label_dy=0.25)
    arrow(ax, 6.2, y_main, 6.8, y_main, label="texts_n1", label_dy=0.25)
    arrow(ax, 9.2, y_main, 9.8, y_main, label="operators_n2", label_dy=0.25)
    arrow(ax, 12.2, y_main, 13.4, y_main, label="properties_n3", label_dy=0.25)

    # Validation (bottom)
    box(
        ax,
        8.0,
        1.4,
        13.5,
        1.6,
        "Pairwise validation (model output $\\times$ reference)\n"
        "9 similarity metrics: FuzzyWuzzy, TF-IDF, SBERT, BERTimbau, Multilingual, WMD_ft, WMD_nilc, BERTScore, ROUGE-L\n"
        "4 classification metrics: Accuracy, Precision, Recall, F1   $\\rightarrow$   metrics/validate_*.json",
        facecolor="#FCE8E6",
        edgecolor="#D93025",
        fontsize=9,
    )

    arrow(ax, 5.0, 4.45, 5.0, 2.25, color="#D93025")
    arrow(ax, 8.0, 4.45, 8.0, 2.25, color="#D93025")
    arrow(ax, 11.0, 4.45, 11.0, 2.25, color="#D93025")

    ax.set_title("Pipeline for converting technical standards into the RASE format", fontsize=12, fontweight="bold", pad=10)
    out = OUT_DIR / "pipeline-en.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print("Generated:", plot_pipeline())
