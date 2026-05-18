from typing import List, Tuple

from tools.generate_tables import generate_tables
from utils.screens.clear_screen import clear_screen
from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_prompt import menu_prompt
from utils.screens.menu_text_line import menu_text_line
from utils.screens.read_single_key import read_single_key
from utils.screens.show_debug_banner import show_debug_banner
from utils.screens.wait_to_return import wait_to_return


def menu_tables() -> None:
    options_n: List[Tuple[str, str, bool]] = [
        ("1", "n1", True),
        ("2", "n2", True),
        ("3", "n3", True),
        ("4", "n1n2", True),
        ("5", "n1n2n3", True),
    ]

    while True:
        show_debug_banner()
        print(menu_bar_line())
        print(menu_text_line("GERAR TABELAS", align_left=False))
        print(menu_bar_line())
        print(
            menu_text_line(
                "Saida: tables/results_<n>_similarity.tex, _classification.tex, .csv"
            )
        )
        print(menu_bar_line())
        for key, name, active in options_n:
            print(menu_text_line(f"{key} - [{'x' if active else ' '}] {name}"))
        print(menu_bar_line())
        print(menu_text_line("Enter - Processar"))
        print(menu_bar_line())
        print(menu_text_line("0 - Voltar", color="red"))
        print(menu_bar_line())
        menu_prompt("Escolha uma opcao: ", color="green")
        print(menu_bar_line())

        choice: str = read_single_key().strip()
        print()

        if choice == "0":
            clear_screen()
            break
        elif choice in {"1", "2", "3", "4", "5"}:
            clear_screen()
            i = int(choice) - 1
            options_n[i] = (options_n[i][0], options_n[i][1], not options_n[i][2])
        elif choice == "":
            clear_screen()
            active_ns: List[str] = [n_key for _, n_key, active in options_n if active]
            if not active_ns:
                print("Selecione o 1, 2, 3, 4 ou 5 para gerar as tabelas.")
                print()
                input("Digite qualquer tecla para voltar ao menu.")
                continue
            generate_tables(levels=active_ns, metrics_dir="metrics", out_dir="tables")
            wait_to_return()
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()
