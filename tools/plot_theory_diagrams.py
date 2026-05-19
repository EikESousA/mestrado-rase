"""Gera as figuras conceituais do capítulo 3 (Fundamentação Teórica) em PNG."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "dissertacao" / "Imagens"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta consistente
C_BLUE = "#1A73E8"
C_GREEN = "#188038"
C_RED = "#D93025"
C_ORANGE = "#E8710A"
C_GRAY = "#5F6368"
C_PURPLE = "#8E24AA"
C_TEAL = "#00838F"

BG_BLUE = "#E8F0FE"
BG_GREEN = "#E6F4EA"
BG_RED = "#FCE8E6"
BG_ORANGE = "#FFF3E0"
BG_GRAY = "#F8F9FA"
BG_PURPLE = "#F3E8FD"


# ---------- Helpers ----------------------------------------------------------


def box(ax, x, y, w, h, text, facecolor=BG_BLUE, edgecolor=C_BLUE,
        fontsize=10, weight="normal", color="black"):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=1.5,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight, color=color)


def arrow(ax, x1, y1, x2, y2, color=C_GRAY, style="->", lw=1.5,
          curve=0.0, label=None, label_offset=(0, 0.18), label_fs=8):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, color=color, linewidth=lw,
        mutation_scale=14,
        connectionstyle=f"arc3,rad={curve}",
    )
    ax.add_patch(arr)
    if label:
        mx, my = (x1 + x2) / 2 + label_offset[0], (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=label_fs, color=color, style="italic")


def setup(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.axis("off")


# ---------- 3.1.1 BIM --------------------------------------------------------


def plot_bim() -> Path:
    fig, ax = plt.subplots(figsize=(10, 7))
    setup(ax, (-5, 5), (-4.2, 4.2))

    # Núcleo
    core = Circle((0, 0), 1.05, facecolor="#202124", edgecolor="black", linewidth=2)
    ax.add_patch(core)
    ax.text(0, 0, "BIM", ha="center", va="center",
            fontsize=18, fontweight="bold", color="white")

    dimensoes = [
        ("3D", "Modelo\nVirtual", BG_BLUE, C_BLUE, 90),
        ("4D", "Programação\n(Tempo)", BG_GREEN, C_GREEN, 162),
        ("5D", "Custos", BG_ORANGE, C_ORANGE, 234),
        ("6D", "Sustentabilidade", BG_PURPLE, C_PURPLE, 306),
        ("7D", "Gerenciamento\nde Instalações", BG_RED, C_RED, 18),
    ]

    r = 2.9
    for dim, label, bg, ec, ang in dimensoes:
        x = r * np.cos(np.radians(ang))
        y = r * np.sin(np.radians(ang))
        c = Circle((x, y), 0.85, facecolor=bg, edgecolor=ec, linewidth=2)
        ax.add_patch(c)
        ax.text(x, y + 0.22, dim, ha="center", va="center",
                fontsize=14, fontweight="bold", color=ec)
        ax.text(x, y - 0.32, label, ha="center", va="center",
                fontsize=8, color="#202124")
        # Conector
        x0 = 1.05 * np.cos(np.radians(ang))
        y0 = 1.05 * np.sin(np.radians(ang))
        x1 = (r - 0.85) * np.cos(np.radians(ang))
        y1 = (r - 0.85) * np.sin(np.radians(ang))
        ax.plot([x0, x1], [y0, y1], color="#9AA0A6", linewidth=1.2, linestyle="--")

    ax.set_title("Dimensões do BIM", fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.1.1-bim.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.3.1 Matriz de Confusão ----------------------------------------


def plot_confusion_matrix() -> Path:
    fig, ax = plt.subplots(figsize=(8, 6))
    setup(ax, (0, 10), (0, 8))

    # Headers
    ax.text(5.0, 7.6, "Valor Real", ha="center", va="center",
            fontsize=12, fontweight="bold")
    ax.text(0.4, 4.0, "Predição", ha="center", va="center",
            fontsize=12, fontweight="bold", rotation=90)

    ax.text(3.75, 6.9, "Positivo", ha="center", va="center", fontsize=11, fontweight="bold")
    ax.text(6.75, 6.9, "Negativo", ha="center", va="center", fontsize=11, fontweight="bold")
    ax.text(1.4, 5.3, "Positivo", ha="center", va="center", fontsize=11, fontweight="bold", rotation=90)
    ax.text(1.4, 2.8, "Negativo", ha="center", va="center", fontsize=11, fontweight="bold", rotation=90)

    # Quatro células
    cells = [
        (2.25, 4.05, 3.0, 2.5, "Verdadeiro\nPositivo\n(TP)", BG_GREEN, C_GREEN),
        (5.25, 4.05, 3.0, 2.5, "Falso\nPositivo\n(FP)", BG_RED, C_RED),
        (2.25, 1.55, 3.0, 2.5, "Falso\nNegativo\n(FN)", BG_RED, C_RED),
        (5.25, 1.55, 3.0, 2.5, "Verdadeiro\nNegativo\n(TN)", BG_GREEN, C_GREEN),
    ]
    for x, y, w, h, txt, bg, ec in cells:
        rect = Rectangle((x, y), w, h, facecolor=bg, edgecolor=ec, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=11, fontweight="bold", color=ec)

    ax.set_title("Matriz de Confusão", fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.3.1-matrizconfusao.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.4.1 Rede Neural MLP -------------------------------------------


def plot_mlp() -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    setup(ax, (0, 10), (0, 6))

    layers = [
        ("Entrada", 1.5, ["$x_1$", "$x_2$", "$x_3$", "$x_4$"], C_ORANGE, BG_ORANGE),
        ("Oculta 1", 4.0, ["$h_1$", "$h_2$", "$h_3$", "$h_4$", "$h_5$"], C_BLUE, BG_BLUE),
        ("Oculta 2", 6.5, ["$h_1$", "$h_2$", "$h_3$", "$h_4$"], C_BLUE, BG_BLUE),
        ("Saída", 9.0, ["$y_1$", "$y_2$"], C_GREEN, BG_GREEN),
    ]

    nodes = []
    for name, x, items, color, bg in layers:
        n = len(items)
        ys = np.linspace(5.0, 1.0, n)
        layer_nodes = []
        for y, lbl in zip(ys, items):
            c = Circle((x, y), 0.28, facecolor=bg, edgecolor=color, linewidth=1.6, zorder=3)
            ax.add_patch(c)
            ax.text(x, y, lbl, ha="center", va="center", fontsize=9, zorder=4)
            layer_nodes.append((x, y))
        ax.text(x, 5.55, name, ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=color)
        nodes.append(layer_nodes)

    # Conexões totalmente conectadas
    for i in range(len(nodes) - 1):
        for (x1, y1) in nodes[i]:
            for (x2, y2) in nodes[i + 1]:
                ax.plot([x1 + 0.28, x2 - 0.28], [y1, y2],
                        color="#BDC1C6", linewidth=0.6, zorder=1)

    ax.set_title("Rede Neural Multicamadas (MLP)",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.4.1-rna.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.4.2 Estrutura de um neurônio ----------------------------------


def plot_neuron() -> Path:
    fig, ax = plt.subplots(figsize=(11, 6))
    setup(ax, (0, 12), (0, 7))

    # Entradas x_i com pesos w_i
    inputs = [("$x_1$", "$w_1$", 5.5), ("$x_2$", "$w_2$", 4.5),
              ("$x_3$", "$w_3$", 3.5), ("$\\vdots$", "$\\vdots$", 2.5),
              ("$x_n$", "$w_n$", 1.5)]

    sum_x, sum_y = 6.5, 3.5
    act_x = 9.0
    out_x = 11.0

    for label_x, label_w, y in inputs:
        ax.text(0.5, y, label_x, ha="center", va="center", fontsize=12)
        ax.annotate("", xy=(sum_x - 0.7, sum_y), xytext=(1.0, y),
                    arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.2))
        # Peso no meio da seta
        mx, my = (1.0 + sum_x - 0.7) / 2, (y + sum_y) / 2
        ax.text(mx, my + 0.15, label_w, ha="center", va="bottom",
                fontsize=10, color=C_BLUE, style="italic",
                bbox=dict(boxstyle="round,pad=0.1", facecolor="white", edgecolor="none"))

    # Bias
    ax.text(sum_x, 6.4, r"$\theta$ (bias)", ha="center", va="center", fontsize=11, color=C_ORANGE)
    ax.annotate("", xy=(sum_x, sum_y + 0.65), xytext=(sum_x, 6.1),
                arrowprops=dict(arrowstyle="->", color=C_ORANGE, lw=1.5))

    # Somatório
    c = Circle((sum_x, sum_y), 0.65, facecolor=BG_BLUE, edgecolor=C_BLUE, linewidth=2)
    ax.add_patch(c)
    ax.text(sum_x, sum_y, "$\\Sigma$", ha="center", va="center", fontsize=18, fontweight="bold")

    # u
    ax.annotate("", xy=(act_x - 0.65, sum_y), xytext=(sum_x + 0.65, sum_y),
                arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.5))
    ax.text((sum_x + act_x) / 2, sum_y + 0.25, "$u$",
            ha="center", va="bottom", fontsize=12, style="italic")

    # Função de ativação
    c2 = Circle((act_x, sum_y), 0.7, facecolor=BG_GREEN, edgecolor=C_GREEN, linewidth=2)
    ax.add_patch(c2)
    ax.text(act_x, sum_y, "$\\varphi(u)$", ha="center", va="center", fontsize=12, fontweight="bold")

    # Saída
    ax.annotate("", xy=(out_x, sum_y), xytext=(act_x + 0.7, sum_y),
                arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.5))
    ax.text(out_x + 0.1, sum_y, "$y$", ha="left", va="center", fontsize=14, fontweight="bold")

    # Legendas
    ax.text(0.5, 6.3, "Entradas", ha="center", va="bottom",
            fontsize=10, fontweight="bold", color=C_GRAY)
    ax.text(sum_x, 1.4, "Soma\nponderada", ha="center", va="center",
            fontsize=9, color=C_BLUE)
    ax.text(act_x, 1.4, "Função de\nativação", ha="center", va="center",
            fontsize=9, color=C_GREEN)

    ax.set_title("Estrutura de um neurônio (MLP)",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.4.2-rnamlp.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.4.3 Bias -------------------------------------------------------


def plot_bias() -> Path:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(-8, 8)
    ax.set_ylim(-0.1, 1.1)

    x = np.linspace(-8, 8, 400)

    def sigmoid(x, b=0.0):
        return 1.0 / (1.0 + np.exp(-(x + b)))

    ax.plot(x, sigmoid(x, b=0), color=C_BLUE, linewidth=2.2, label=r"$\theta = 0$")
    ax.plot(x, sigmoid(x, b=3), color=C_GREEN, linewidth=2.2,
            linestyle="--", label=r"$\theta = +3$ (desloca à esquerda)")
    ax.plot(x, sigmoid(x, b=-3), color=C_RED, linewidth=2.2,
            linestyle="--", label=r"$\theta = -3$ (desloca à direita)")

    ax.axhline(0.5, color="#BDC1C6", linewidth=0.8, linestyle=":")
    ax.axvline(0, color="#BDC1C6", linewidth=0.8, linestyle=":")

    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel(r"$\varphi(x + \theta)$", fontsize=11)
    ax.set_title("Deslocamento da função sigmoide pela constante bias",
                 fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="lower right", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.25)

    out = OUT_DIR / "3.4.3-bias.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.4.4 Tipos de Redes ---------------------------------------------


def _draw_network(ax, layers, recurrent=False, title=""):
    """Helper para desenhar redes (a) (b) (c) (d)."""
    n_layers = len(layers)
    xs = np.linspace(0.5, 3.5, n_layers)
    positions = []
    for x, n in zip(xs, layers):
        ys = np.linspace(2.7, 0.4, n) if n > 1 else [1.55]
        col = []
        for y in ys:
            c = Circle((x, y), 0.18, facecolor=BG_BLUE, edgecolor=C_BLUE, linewidth=1.4, zorder=3)
            ax.add_patch(c)
            col.append((x, y))
        positions.append(col)

    for i in range(n_layers - 1):
        for (x1, y1) in positions[i]:
            for (x2, y2) in positions[i + 1]:
                ax.plot([x1 + 0.18, x2 - 0.18], [y1, y2],
                        color="#9AA0A6", linewidth=0.7, zorder=1)

    if recurrent:
        # Setas de realimentação da saída para a entrada (passando por baixo)
        for k, (x2, y2) in enumerate(positions[-1]):
            for (x1, y1) in positions[0]:
                arc = FancyArrowPatch(
                    (x2, y2 - 0.18), (x1, y1 - 0.18),
                    arrowstyle="->", color=C_RED, linewidth=1.0,
                    mutation_scale=10,
                    connectionstyle=f"arc3,rad=-{0.45 + 0.1 * k}",
                    zorder=2,
                )
                ax.add_patch(arc)

    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlim(0, 4)
    ax.set_ylim(-1.4, 3.4)
    ax.set_aspect("equal")
    ax.axis("off")


def plot_network_types() -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    _draw_network(axes[0][0], [3, 2], recurrent=False,
                  title="(a) Camada única — feedforward")
    _draw_network(axes[0][1], [3, 4, 2], recurrent=False,
                  title="(b) Múltiplas camadas — feedforward")
    _draw_network(axes[1][0], [3, 2], recurrent=True,
                  title="(c) Camada única — recorrente")
    _draw_network(axes[1][1], [3, 4, 2], recurrent=True,
                  title="(d) Múltiplas camadas — recorrente")

    fig.suptitle("Tipos de camadas e conexões de nodos",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = OUT_DIR / "3.4.4-tiposrna.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.5.3 Word Embeddings -------------------------------------------


def plot_word_embeddings() -> Path:
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    palavras = [
        ("gato",       (0.18, 0.22, 0.85), C_BLUE),
        ("gatinho",    (0.15, 0.08, 0.78), C_BLUE),
        ("cão",        (0.40, 0.32, 0.32), C_ORANGE),
        ("filhote",    (0.25, 0.12, 0.55), C_ORANGE),
        ("gorila",     (0.72, 0.78, 0.10), C_GREEN),
        ("macaco",     (0.62, 0.45, 0.18), C_GREEN),
        ("formiga",    (0.90, 0.05, 0.05), C_RED),
        ("elefante",   (0.55, 0.95, 0.50), C_PURPLE),
    ]

    for nome, (x, y, z), c in palavras:
        ax.scatter([x], [y], [z], color=c, s=120, edgecolor="black", linewidth=0.6)
        ax.text(x + 0.02, y + 0.02, z + 0.03, nome, fontsize=10, fontweight="bold")

    ax.set_xlabel("morfológica", fontsize=10)
    ax.set_ylabel("tamanho", fontsize=10)
    ax.set_zlabel("cor", fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_zlim(0, 1)
    ax.set_title("Word Embeddings (3 dimensões)",
                 fontsize=12, fontweight="bold", pad=10)

    out = OUT_DIR / "3.5.3-wordembeddings.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.5.4 Sentence Embeddings ---------------------------------------


def plot_sentence_embeddings() -> Path:
    fig, ax = plt.subplots(figsize=(11, 6))
    setup(ax, (0, 13), (0, 7))

    sentenca = ["O", "gato", "preto", "dorme"]

    # Frase
    for i, w in enumerate(sentenca):
        box(ax, 1.5 + i * 1.6, 6.0, 1.3, 0.7, w,
            facecolor=BG_ORANGE, edgecolor=C_ORANGE, fontsize=11, weight="bold")

    # Word embeddings (colunas de números)
    np.random.seed(0)
    for i, w in enumerate(sentenca):
        x = 1.5 + i * 1.6
        vec = np.random.uniform(-1, 1, size=5)
        rect = Rectangle((x - 0.5, 3.6), 1.0, 1.6,
                         facecolor=BG_BLUE, edgecolor=C_BLUE, linewidth=1.5)
        ax.add_patch(rect)
        for j, v in enumerate(vec):
            ax.text(x, 4.95 - j * 0.32, f"{v:+.2f}",
                    ha="center", va="center", fontsize=8, family="monospace")
        # Seta
        arrow(ax, x, 5.6, x, 5.25)
        ax.text(x, 3.35, f"$w_{i+1}$", ha="center", va="center",
                fontsize=10, fontstyle="italic", color=C_BLUE)

    # Agregação
    ax.text(8.7, 4.4, "→  agrega  →", ha="center", va="center",
            fontsize=12, fontweight="bold", color=C_GRAY)

    # Sentence embedding
    rect = Rectangle((10.2, 3.6), 2.0, 1.6,
                     facecolor=BG_GREEN, edgecolor=C_GREEN, linewidth=2)
    ax.add_patch(rect)
    vec = np.random.uniform(-1, 1, size=5)
    for j, v in enumerate(vec):
        ax.text(11.2, 4.95 - j * 0.32, f"{v:+.2f}",
                ha="center", va="center", fontsize=8, family="monospace")
    ax.text(11.2, 3.0, "sentence embedding", ha="center", va="center",
            fontsize=10, fontweight="bold", color=C_GREEN)

    ax.text(4.5, 6.85, "Frase", ha="center", fontsize=11, fontweight="bold", color=C_ORANGE)
    ax.text(4.5, 2.45, "Word embeddings de cada token", ha="center", fontsize=10, color=C_BLUE)

    ax.set_title("De Word Embeddings para Sentence Embeddings",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.5.4-sentenceembeddings.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.6.1 Seq2Seq ---------------------------------------------------


def plot_seq2seq() -> Path:
    fig, ax = plt.subplots(figsize=(14, 6))
    setup(ax, (0, 16), (0, 7))

    # Encoder
    ax.text(0.5, 6.2, "Encoder (RNN)", fontsize=11, fontweight="bold", color=C_BLUE)
    enc_words = ["I", "have", "to", "go"]
    for i, w in enumerate(enc_words):
        x = 1.5 + i * 1.5
        box(ax, x, 4.5, 1.0, 0.9, "RNN", facecolor=BG_BLUE, edgecolor=C_BLUE, fontsize=10)
        ax.text(x, 5.6, w, ha="center", va="center", fontsize=11, fontweight="bold", color=C_ORANGE)
        arrow(ax, x, 5.3, x, 4.95, color=C_ORANGE)
        if i > 0:
            arrow(ax, 1.5 + (i - 1) * 1.5 + 0.5, 4.5, x - 0.5, 4.5)

    # Contexto
    ctx_x = 8.5
    box(ax, ctx_x, 4.5, 1.6, 1.0, "Contexto",
        facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=10, weight="bold")
    arrow(ax, 1.5 + 3 * 1.5 + 0.5, 4.5, ctx_x - 0.8, 4.5, color=C_GRAY, lw=2)

    # Decoder
    ax.text(10.0, 6.2, "Decoder (RNN)", fontsize=11, fontweight="bold", color=C_GREEN)
    dec_words = ["Eu", "tenho", "que", "ir"]
    for i, w in enumerate(dec_words):
        x = 11.0 + i * 1.1
        box(ax, x, 4.5, 0.9, 0.9, "RNN", facecolor=BG_GREEN, edgecolor=C_GREEN, fontsize=9)
        ax.text(x, 3.4, w, ha="center", va="center", fontsize=11, fontweight="bold", color=C_GREEN)
        arrow(ax, x, 4.05, x, 3.65, color=C_GREEN)
        if i > 0:
            arrow(ax, 11.0 + (i - 1) * 1.1 + 0.45, 4.5, x - 0.45, 4.5)
    arrow(ax, ctx_x + 0.8, 4.5, 11.0 - 0.45, 4.5, color=C_GRAY, lw=2)

    ax.text(4.5, 6.85, "Frase em inglês (entrada)", ha="center",
            fontsize=10, color=C_ORANGE, fontweight="bold")
    ax.text(12.65, 2.7, "Frase em português (saída)", ha="center",
            fontsize=10, color=C_GREEN, fontweight="bold")

    ax.set_title("Modelo seq2seq — tradução inglês → português",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.6.1-seq2seq.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.6.2 Attention -------------------------------------------------


def plot_attention() -> Path:
    fig, ax = plt.subplots(figsize=(14, 7))
    setup(ax, (0, 16), (0, 8))

    # Encoder estados ocultos
    enc_words = ["I", "have", "to", "go"]
    enc_x = [1.5, 3.0, 4.5, 6.0]
    for x, w in zip(enc_x, enc_words):
        ax.text(x, 6.9, w, ha="center", va="center",
                fontsize=11, fontweight="bold", color=C_ORANGE)
        arrow(ax, x, 6.6, x, 6.15, color=C_ORANGE)
        box(ax, x, 5.7, 0.95, 0.8, "RNN",
            facecolor=BG_BLUE, edgecolor=C_BLUE, fontsize=9)
    for i in range(3):
        arrow(ax, enc_x[i] + 0.48, 5.7, enc_x[i + 1] - 0.48, 5.7)

    # Estados ocultos h_i
    for i, x in enumerate(enc_x):
        box(ax, x, 4.4, 0.8, 0.55, f"$h_{i+1}$",
            facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=10)
        arrow(ax, x, 5.3, x, 4.7)

    # Pesos de atenção (linhas para o decoder)
    dec_x = 10.5
    dec_y = 4.4
    box(ax, dec_x, dec_y, 1.4, 0.8, "Atenção\n($\\alpha_i$)",
        facecolor="#FFF8DC", edgecolor=C_ORANGE, fontsize=9, weight="bold")
    for i, x in enumerate(enc_x):
        alpha = [0.1, 0.25, 0.2, 0.45][i]
        arr = FancyArrowPatch(
            (x + 0.4, 4.4), (dec_x - 0.7, dec_y),
            arrowstyle="->", color=C_RED, linewidth=alpha * 4 + 0.4,
            mutation_scale=10, alpha=0.6 + alpha * 0.5,
            connectionstyle="arc3,rad=0.1",
        )
        ax.add_patch(arr)
        ax.text((x + dec_x) / 2, 4.4 + 0.2 + i * 0.05,
                f"$\\alpha_{i+1}$={alpha:.2f}",
                fontsize=7, color=C_RED, alpha=0.9)

    # Contexto dinâmico
    box(ax, dec_x, 3.0, 1.4, 0.6, "Contexto $c_t$",
        facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=9)
    arrow(ax, dec_x, 4.0, dec_x, 3.3, color=C_GRAY)

    # Decoder
    box(ax, dec_x, 1.8, 1.0, 0.9, "RNN dec.",
        facecolor=BG_GREEN, edgecolor=C_GREEN, fontsize=9)
    arrow(ax, dec_x, 2.7, dec_x, 2.3, color=C_GREEN)
    arrow(ax, dec_x, 1.3, dec_x, 0.6, color=C_GREEN)
    ax.text(dec_x, 0.35, "tenho", ha="center", va="center",
            fontsize=11, fontweight="bold", color=C_GREEN)

    # Entrada anterior do decoder
    box(ax, dec_x - 2.0, 1.8, 1.0, 0.9, "Eu",
        facecolor=BG_GREEN, edgecolor=C_GREEN, fontsize=10)
    arrow(ax, dec_x - 1.5, 1.8, dec_x - 0.5, 1.8, color=C_GREEN)

    ax.text(3.75, 7.6, "Encoder — frase em inglês",
            ha="center", fontsize=11, fontweight="bold", color=C_BLUE)
    ax.text(dec_x, 7.6, "Decoder — atenção dinâmica sobre os $h_i$",
            ha="center", fontsize=11, fontweight="bold", color=C_GREEN)

    ax.set_title("Mecanismo de atenção em seq2seq",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.6.2-attention.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.6.3 Self-Attention --------------------------------------------


def plot_self_attention() -> Path:
    fig, ax = plt.subplots(figsize=(13, 9))
    setup(ax, (0, 14), (0, 11))

    # (a) palavras de entrada
    palavras = ["Eu", "estou", "feliz"]
    palavra_x = [2.0, 6.0, 10.0]
    for x, w in zip(palavra_x, palavras):
        box(ax, x, 10.0, 1.4, 0.7, w,
            facecolor=BG_ORANGE, edgecolor=C_ORANGE, fontsize=11, weight="bold")
    ax.text(0.5, 10.0, "(a)", fontsize=10, fontweight="bold", color=C_GRAY)

    # (b)(c)(d) Q K V vetores
    matrizes = [("$W^Q$", "$q$", C_BLUE, BG_BLUE, "(b)"),
                ("$W^K$", "$k$", C_GREEN, BG_GREEN, "(c)"),
                ("$W^V$", "$v$", C_PURPLE, BG_PURPLE, "(d)")]

    for idx, (W, vec, c, bg, tag) in enumerate(matrizes):
        y_top = 8.6
        ax.text(0.2, y_top - idx * 1.0, tag, fontsize=10, fontweight="bold", color=C_GRAY)
        for k_idx, x in enumerate(palavra_x):
            if k_idx > 0:
                ax.text(x - 1.4, y_top - idx * 1.0, "×",
                        fontsize=14, ha="center", color=C_GRAY)
            box(ax, x - 0.85, y_top - idx * 1.0, 0.7, 0.55, W,
                facecolor="#FFFFFF", edgecolor=c, fontsize=9)
            ax.text(x - 0.25, y_top - idx * 1.0, "=", fontsize=14, ha="center", color=C_GRAY)
            box(ax, x + 0.35, y_top - idx * 1.0, 0.55, 0.55, vec,
                facecolor=bg, edgecolor=c, fontsize=10, weight="bold")

    # (e) Score = q · k
    ax.text(0.5, 5.0, "(e)", fontsize=10, fontweight="bold", color=C_GRAY)
    ax.text(7.0, 5.0, r"$\mathrm{score}_{ij} = q_i \cdot k_j$",
            ha="center", va="center", fontsize=13, color=C_RED,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_RED, edgecolor=C_RED))

    # (g) divisão e (h) softmax
    ax.text(0.5, 3.7, "(g)", fontsize=10, fontweight="bold", color=C_GRAY)
    ax.text(4.5, 3.7, r"÷ $\sqrt{d_k}$",
            ha="center", va="center", fontsize=12, color=C_GRAY,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=BG_GRAY, edgecolor=C_GRAY))
    ax.text(0.5, 2.6, "(h)", fontsize=10, fontweight="bold", color=C_GRAY)
    ax.text(7.0, 2.6, r"$\alpha_{ij} = \mathrm{softmax}(\mathrm{score}_{ij}/\sqrt{d_k})$",
            ha="center", va="center", fontsize=12, color=C_ORANGE,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF3E0", edgecolor=C_ORANGE))

    # (i) s_ij = alpha * v
    ax.text(0.5, 1.4, "(i)", fontsize=10, fontweight="bold", color=C_GRAY)
    ax.text(4.5, 1.4, r"$s_{ij} = \alpha_{ij} \cdot v_j$",
            ha="center", va="center", fontsize=12, color=C_PURPLE,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=BG_PURPLE, edgecolor=C_PURPLE))

    # (j) z = soma
    ax.text(0.5, 0.3, "(j)", fontsize=10, fontweight="bold", color=C_GRAY)
    ax.text(9.5, 1.4, r"$z_i = \sum_j s_{ij}$",
            ha="center", va="center", fontsize=13, fontweight="bold", color=C_GREEN,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_GREEN, edgecolor=C_GREEN))

    ax.set_title("Cálculo da camada self-attention",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.6.3-selfattention.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.6.4 Transformer Stack -----------------------------------------


def plot_transformer_stack() -> Path:
    fig, ax = plt.subplots(figsize=(11, 8))
    setup(ax, (0, 12), (0, 10))

    # Entrada (texto inglês)
    box(ax, 2.5, 0.6, 3.0, 0.7, "I have to go",
        facecolor=BG_ORANGE, edgecolor=C_ORANGE, fontsize=11, weight="bold")
    box(ax, 2.5, 1.6, 3.0, 0.55, "Input Embeddings + Pos. Encoding",
        facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=8)
    arrow(ax, 2.5, 0.95, 2.5, 1.3, color=C_ORANGE)

    # Stack de encoders
    for i in range(6):
        y = 2.6 + i * 0.85
        box(ax, 2.5, y, 3.0, 0.7, f"Encoder {6 - i}",
            facecolor=BG_BLUE, edgecolor=C_BLUE, fontsize=10)
    arrow(ax, 2.5, 1.9, 2.5, 2.25, color=C_BLUE)

    # Stack de decoders
    for i in range(6):
        y = 2.6 + i * 0.85
        box(ax, 7.5, y, 3.0, 0.7, f"Decoder {6 - i}",
            facecolor=BG_GREEN, edgecolor=C_GREEN, fontsize=10)

    # Entrada do decoder
    box(ax, 7.5, 0.6, 3.0, 0.7, "<start> ...",
        facecolor=BG_GREEN, edgecolor=C_GREEN, fontsize=10)
    box(ax, 7.5, 1.6, 3.0, 0.55, "Output Embeddings + Pos. Encoding",
        facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=8)
    arrow(ax, 7.5, 0.95, 7.5, 1.3, color=C_GREEN)
    arrow(ax, 7.5, 1.9, 7.5, 2.25, color=C_GREEN)

    # Conexão encoder → decoder (saída do último encoder)
    arr = FancyArrowPatch(
        (4.0, 7.7), (6.0, 7.7),
        arrowstyle="->", color=C_GRAY, linewidth=1.8,
        mutation_scale=14,
    )
    ax.add_patch(arr)
    ax.text(5.0, 7.95, "K, V (contexto)", ha="center",
            fontsize=8, style="italic", color=C_GRAY)

    # Saída final (linear + softmax)
    box(ax, 7.5, 8.5, 3.0, 0.55, "Linear + Softmax",
        facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=9)
    arrow(ax, 7.5, 8.05, 7.5, 8.2, color=C_GREEN)

    # Token gerado
    box(ax, 7.5, 9.5, 3.0, 0.6, "tenho",
        facecolor="#FFF8DC", edgecolor=C_ORANGE, fontsize=11, weight="bold")
    # Seta azul - saída
    arr_blue = FancyArrowPatch(
        (7.5, 8.78), (7.5, 9.2),
        arrowstyle="->", color=C_BLUE, linewidth=2.0,
        mutation_scale=16,
    )
    ax.add_patch(arr_blue)

    # Seta amarela - feedback do output
    arr_y = FancyArrowPatch(
        (9.0, 9.5), (9.0, 0.6),
        arrowstyle="->", color="#F9AB00", linewidth=1.8,
        mutation_scale=14, connectionstyle="arc3,rad=0.45",
    )
    ax.add_patch(arr_y)
    ax.text(11.0, 5.0, "feedback\n(autoregressivo)", fontsize=8,
            color="#F9AB00", ha="center", style="italic")

    ax.text(2.5, 9.5, "Encoder Stack (6×)",
            ha="center", fontsize=11, fontweight="bold", color=C_BLUE)
    ax.text(7.5, 9.95, "Decoder Stack (6×) →",
            ha="center", fontsize=11, fontweight="bold", color=C_GREEN)

    ax.set_title("Pilha do Transformer (encoders e decoders)",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.6.4-transformer.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.6.5 Camadas Transformer ---------------------------------------


def plot_transformer_layers() -> Path:
    fig, ax = plt.subplots(figsize=(13, 8.5))
    setup(ax, (0, 14), (0, 10))

    # Encoder
    enc_layers = [
        ("Multi-Head Self-Attention", BG_BLUE, C_BLUE, 2.0),
        ("Add & Norm", BG_GRAY, C_GRAY, 3.2),
        ("Feed Forward", BG_BLUE, C_BLUE, 4.4),
        ("Add & Norm", BG_GRAY, C_GRAY, 5.6),
    ]
    for txt, bg, ec, y in enc_layers:
        box(ax, 3.0, y, 4.0, 0.8, txt,
            facecolor=bg, edgecolor=ec, fontsize=10, weight="bold")
    for y_from, y_to in [(0.95, 1.6), (2.4, 2.8), (3.6, 4.0), (4.8, 5.2), (6.0, 6.6)]:
        arrow(ax, 3.0, y_from, 3.0, y_to, color=C_BLUE)

    # Input do encoder
    box(ax, 3.0, 0.6, 4.0, 0.7, "Input Embedding + Pos. Encoding",
        facecolor=BG_ORANGE, edgecolor=C_ORANGE, fontsize=9, weight="bold")

    ax.text(3.0, 6.95, "ENCODER", ha="center",
            fontsize=12, fontweight="bold", color=C_BLUE)

    # Decoder
    dec_layers = [
        ("Masked Multi-Head\nSelf-Attention", BG_GREEN, C_GREEN, 2.0),
        ("Add & Norm", BG_GRAY, C_GRAY, 3.0),
        ("Encoder-Decoder\nAttention", "#FFF8DC", C_ORANGE, 4.1),
        ("Add & Norm", BG_GRAY, C_GRAY, 5.1),
        ("Feed Forward", BG_GREEN, C_GREEN, 6.1),
        ("Add & Norm", BG_GRAY, C_GRAY, 7.1),
    ]
    for txt, bg, ec, y in dec_layers:
        h = 0.95 if "\n" in txt else 0.7
        box(ax, 9.5, y, 4.0, h, txt,
            facecolor=bg, edgecolor=ec, fontsize=9, weight="bold")
    for y_from, y_to in [(0.95, 1.45), (2.55, 2.7), (3.35, 3.6), (4.6, 4.8),
                          (5.45, 5.8), (6.45, 6.8), (7.45, 8.0)]:
        arrow(ax, 9.5, y_from, 9.5, y_to, color=C_GREEN)

    # Input do decoder
    box(ax, 9.5, 0.6, 4.0, 0.7, "Output Embedding + Pos. Encoding",
        facecolor=BG_ORANGE, edgecolor=C_ORANGE, fontsize=9, weight="bold")

    # Linear + Softmax + Output
    box(ax, 9.5, 8.3, 4.0, 0.6, "Linear + Softmax",
        facecolor=BG_GRAY, edgecolor=C_GRAY, fontsize=9)
    box(ax, 9.5, 9.3, 4.0, 0.65, "Output probabilities",
        facecolor="#FFF8DC", edgecolor=C_ORANGE, fontsize=10, weight="bold")
    arrow(ax, 9.5, 8.6, 9.5, 8.95, color=C_ORANGE)

    ax.text(9.5, 9.7 + 0.1, "DECODER", ha="center",
            fontsize=12, fontweight="bold", color=C_GREEN)

    # Conexão encoder -> encoder-decoder attention (K, V)
    arr = FancyArrowPatch(
        (5.0, 4.4), (7.5, 4.1),
        arrowstyle="->", color=C_GRAY, linewidth=1.6,
        mutation_scale=14, connectionstyle="arc3,rad=-0.2",
    )
    ax.add_patch(arr)
    ax.text(6.25, 4.6, "K, V", ha="center", fontsize=9,
            style="italic", color=C_GRAY)

    ax.set_title("Camadas internas do encoder e decoder do Transformer",
                 fontsize=13, fontweight="bold", pad=10)
    out = OUT_DIR / "3.6.5-camadastransformer.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3.8.1 RASE -------------------------------------------------------


def plot_rase() -> Path:
    fig, ax = plt.subplots(figsize=(13, 8.5))
    setup(ax, (0, 14), (0, 10))

    # Texto original com destaque por operador
    ax.text(7.0, 9.5, "Aplicação da metodologia RASE — NBR 9050",
            ha="center", fontsize=13, fontweight="bold", color="#202124")

    # Sentença anotada
    spans = [
        ("A", "Pisos", C_GREEN, BG_GREEN),
        ("S", "internos", C_RED, BG_RED),
        ("R", "devem ter inclinação transversal", C_BLUE, BG_BLUE),
        ("R", "menor ou igual a 2%", C_BLUE, BG_BLUE),
        ("E", "exceto rampas (≥ 5%)", C_ORANGE, BG_ORANGE),
    ]

    y_phrase = 7.6
    x_cursor = 0.7
    for tag, content, ec, bg in spans:
        w = max(1.3, len(content) * 0.13 + 0.4)
        rect = Rectangle((x_cursor, y_phrase - 0.45), w, 0.9,
                         facecolor=bg, edgecolor=ec, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x_cursor + 0.18, y_phrase + 0.25, tag,
                ha="left", va="center", fontsize=9, fontweight="bold", color=ec)
        ax.text(x_cursor + w / 2, y_phrase - 0.05, content,
                ha="center", va="center", fontsize=9.5, color="#202124")
        x_cursor += w + 0.15

    # Legenda das cores
    legenda = [
        ("R — Requisito", C_BLUE, BG_BLUE),
        ("A — Aplicabilidade", C_GREEN, BG_GREEN),
        ("S — Seleção", C_RED, BG_RED),
        ("E — Exceção", C_ORANGE, BG_ORANGE),
    ]
    for i, (txt, ec, bg) in enumerate(legenda):
        rect = Rectangle((0.5 + i * 3.3, 6.0), 3.0, 0.55,
                         facecolor=bg, edgecolor=ec, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(0.5 + i * 3.3 + 1.5, 6.275, txt,
                ha="center", va="center", fontsize=9.5, fontweight="bold", color=ec)

    # Tabela de atributos
    headers = ["Operador", "Objeto", "Propriedade", "Comparador", "Valor", "Unidade"]
    rows = [
        ["A", "Pisos", "—", "—", "—", "—"],
        ["S", "Pisos", "tipo", "=", "internos", "—"],
        ["R", "Pisos", "inclinação\ntransversal", "≤", "2", "%"],
        ["E", "Rampas", "inclinação\nlongitudinal", "≥", "5", "%"],
    ]

    n_cols = len(headers)
    table_x0 = 0.6
    table_y0 = 0.6
    col_w = [1.4, 1.5, 2.2, 1.6, 1.5, 1.4]
    row_h = 0.85

    # Cabeçalho
    x = table_x0
    for i, h in enumerate(headers):
        rect = Rectangle((x, table_y0 + len(rows) * row_h), col_w[i], row_h,
                         facecolor="#202124", edgecolor="#202124")
        ax.add_patch(rect)
        ax.text(x + col_w[i] / 2, table_y0 + len(rows) * row_h + row_h / 2,
                h, ha="center", va="center",
                fontsize=10, fontweight="bold", color="white")
        x += col_w[i]

    # Linhas
    color_map = {"R": (BG_BLUE, C_BLUE),
                 "A": (BG_GREEN, C_GREEN),
                 "S": (BG_RED, C_RED),
                 "E": (BG_ORANGE, C_ORANGE)}
    for r_idx, row in enumerate(rows):
        y = table_y0 + (len(rows) - 1 - r_idx) * row_h
        bg, ec = color_map.get(row[0], ("white", "#202124"))
        x = table_x0
        for c_idx, cell in enumerate(row):
            facecolor = bg if c_idx == 0 else "white"
            rect = Rectangle((x, y), col_w[c_idx], row_h,
                             facecolor=facecolor, edgecolor="#9AA0A6", linewidth=0.8)
            ax.add_patch(rect)
            fontw = "bold" if c_idx == 0 else "normal"
            col = ec if c_idx == 0 else "#202124"
            ax.text(x + col_w[c_idx] / 2, y + row_h / 2, cell,
                    ha="center", va="center", fontsize=9.5,
                    fontweight=fontw, color=col)
            x += col_w[c_idx]

    ax.text(7.0, 5.2, "Extração dos atributos de cada operador RASE",
            ha="center", fontsize=10, fontweight="bold", color=C_GRAY)

    out = OUT_DIR / "3.8.1-rase.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- Main -------------------------------------------------------------


def main() -> None:
    plots = [
        plot_bim,
        plot_confusion_matrix,
        plot_mlp,
        plot_neuron,
        plot_bias,
        plot_network_types,
        plot_word_embeddings,
        plot_sentence_embeddings,
        plot_seq2seq,
        plot_attention,
        plot_self_attention,
        plot_transformer_stack,
        plot_transformer_layers,
        plot_rase,
    ]
    print("Gerando figuras do capítulo 3:")
    for fn in plots:
        path = fn()
        print(" -", path.name)


if __name__ == "__main__":
    main()
