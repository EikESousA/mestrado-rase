"""Recria a figura 14 (Utilização da metodologia RASE na NBR 9050).

A figura tem dois blocos com mesma largura total:
 - Topo: três caixas coloridas (A, S, R) representando os operadores RASE
   aplicados à frase de exemplo extraída da NBR 9050.
 - Base: tabela com os atributos estruturados (Tipo, Objeto, Propriedade,
   Comparador, Valor, Unidade).
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


OUT_PATH = Path(__file__).resolve().parents[1] / "dissertacao" / "Imagens" / "3.8.1-rase.png"

# Cores padronizadas pela metodologia RASE.
COLOR_A = "#3CB371"  # Aplicabilidade — verde
COLOR_S = "#E74C3C"  # Seleção        — vermelho
COLOR_R = "#3498DB"  # Requisito      — azul
COLOR_E = "#E67E22"  # Exceção        — laranja (não usado neste exemplo)

# Conteúdo dos três operadores no exemplo.
operators = [
    {
        "tag": "A",
        "name": "Aplicabilidade",
        "text": "Pisos",
        "color": COLOR_A,
        "weight": 1.0,
    },
    {
        "tag": "S",
        "name": "Seleção",
        "text": "internos",
        "color": COLOR_S,
        "weight": 1.4,
    },
    {
        "tag": "R",
        "name": "Requisito",
        "text": "devem ter inclinação transversal\nmenor ou igual a 2\\%",
        "color": COLOR_R,
        "weight": 3.6,
    },
]

# Linhas da tabela inferior — uma por operador.
table_rows = [
    ["A", "piso", "—", "—", "—", "—"],
    ["S", "piso", "tipo", "=", "interno", "—"],
    ["R", "piso", "inclinação transversal", "≤", "2", "%"],
]
table_header = ["Tipo", "Objeto", "Propriedade", "Comparador", "Valor", "Unidade"]


def build_figure() -> None:
    total_weight = sum(op["weight"] for op in operators)
    width_units = 12.0  # unidades arbitrárias para o eixo x
    column_widths = [op["weight"] / total_weight * width_units for op in operators]

    fig, ax = plt.subplots(figsize=(11, 5), dpi=200)
    ax.set_xlim(0, width_units)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # --- Bloco superior: caixas dos operadores -------------------------------
    box_y = 5.0
    box_height = 1.8
    header_h = 0.55
    x_cursor = 0.0
    for op, width in zip(operators, column_widths):
        # Corpo da caixa (cor mais clara).
        body = Rectangle(
            (x_cursor, box_y),
            width,
            box_height - header_h,
            facecolor=op["color"],
            edgecolor="black",
            linewidth=1.2,
            alpha=0.85,
        )
        ax.add_patch(body)
        # Faixa de cabeçalho mais escura no topo da caixa.
        header = Rectangle(
            (x_cursor, box_y + box_height - header_h),
            width,
            header_h,
            facecolor=op["color"],
            edgecolor="black",
            linewidth=1.2,
        )
        ax.add_patch(header)
        # Título: "A — Aplicabilidade".
        ax.text(
            x_cursor + width / 2,
            box_y + box_height - header_h / 2,
            f"{op['tag']} — {op['name']}",
            color="white",
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="center",
        )
        # Texto principal do operador centralizado no corpo.
        ax.text(
            x_cursor + width / 2,
            box_y + (box_height - header_h) / 2,
            op["text"].replace("\\%", "%"),
            color="white",
            fontsize=11,
            ha="center",
            va="center",
            wrap=True,
        )
        x_cursor += width

    # Frase original acima das caixas.
    ax.text(
        width_units / 2,
        box_y + box_height + 0.45,
        "Frase original: \"Pisos internos devem ter inclinação transversal "
        "menor ou igual a 2%\"",
        color="black",
        fontsize=10,
        style="italic",
        ha="center",
        va="bottom",
    )

    # --- Bloco inferior: tabela estruturada ----------------------------------
    table_y_top = 4.2
    table_height = 3.6
    row_height = table_height / (len(table_rows) + 1)  # +1 para o cabeçalho
    n_cols = len(table_header)
    col_width = width_units / n_cols

    # Cabeçalho.
    header_y = table_y_top - row_height
    for i, label in enumerate(table_header):
        rect = Rectangle(
            (i * col_width, header_y),
            col_width,
            row_height,
            facecolor="#34495E",
            edgecolor="black",
            linewidth=1.0,
        )
        ax.add_patch(rect)
        ax.text(
            i * col_width + col_width / 2,
            header_y + row_height / 2,
            label,
            color="white",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
        )

    # Linhas (primeiro o "Tipo" sai colorido conforme operador).
    type_colors = {"A": COLOR_A, "S": COLOR_S, "R": COLOR_R, "E": COLOR_E}
    for row_idx, row in enumerate(table_rows):
        y = header_y - (row_idx + 1) * row_height
        for col_idx, value in enumerate(row):
            if col_idx == 0:
                face = type_colors.get(value, "white")
                text_color = "white"
                weight = "bold"
            else:
                face = "white" if row_idx % 2 == 0 else "#F4F6F7"
                text_color = "black"
                weight = "normal"
            rect = Rectangle(
                (col_idx * col_width, y),
                col_width,
                row_height,
                facecolor=face,
                edgecolor="black",
                linewidth=0.8,
            )
            ax.add_patch(rect)
            ax.text(
                col_idx * col_width + col_width / 2,
                y + row_height / 2,
                value,
                color=text_color,
                fontsize=10,
                fontweight=weight,
                ha="center",
                va="center",
            )

    # Conectores entre o centro de cada caixa do operador e a célula "Tipo"
    # correspondente na tabela inferior. Linha contínua e fina para ficar
    # discreta sem poluir a figura.
    op_centers = []
    x_cursor = 0.0
    for width in column_widths:
        op_centers.append(x_cursor + width / 2)
        x_cursor += width

    op_bottom_y = box_y
    type_col_center_x = col_width / 2  # todas as setas apontam para a coluna "Tipo".
    for op_idx, op in enumerate(operators):
        x_top = op_centers[op_idx]
        y_bottom = header_y - (op_idx + 1) * row_height + row_height / 2
        ax.annotate(
            "",
            xy=(type_col_center_x, y_bottom + row_height / 2),
            xytext=(x_top, op_bottom_y),
            arrowprops=dict(
                arrowstyle="-|>",
                color=op["color"],
                linewidth=1.0,
                connectionstyle="arc3,rad=0.0",
                alpha=0.75,
            ),
        )

    fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PATH, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Figura salva em {OUT_PATH}")


if __name__ == "__main__":
    build_figure()
