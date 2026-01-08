from typing import List, Tuple

from validates.validate_n1 import validate_n1
from validates.validate_n2 import validate_n2
from utils.screens.clear_screen import clear_screen
from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_prompt import menu_prompt
from utils.screens.menu_text_line import menu_text_line
from utils.screens.read_single_key import read_single_key
from utils.screens.show_debug_banner import show_debug_banner
from utils.screens.wait_to_return import wait_to_return


def menu_validate() -> None:
    options_n: List[Tuple[str, str, bool]] = [
        ("1", "n1", True),
        ("2", "n2", False),
        ("3", "n3", False),
        ("4", "n1_n2", False),
        ("5", "n2_n3", False),
        ("6", "n1_n2_n3", False),
    ]

    while True:
        show_debug_banner()
        print(menu_bar_line())
        print(menu_text_line("VALIDAR DADOS", align_left=False))
        print(menu_bar_line())
        print(menu_text_line(f"1 - [{'x' if options_n[0][2] else ' '}] {options_n[0][1]}"))
        print(menu_text_line(f"2 - [{'x' if options_n[1][2] else ' '}] {options_n[1][1]}"))
        print(menu_text_line(f"3 - [{'x' if options_n[2][2] else ' '}] {options_n[2][1]}"))
        print(menu_text_line(f"4 - [{'x' if options_n[3][2] else ' '}] {options_n[3][1]}"))
        print(menu_text_line(f"5 - [{'x' if options_n[4][2] else ' '}] {options_n[4][1]}"))
        print(menu_text_line(f"6 - [{'x' if options_n[5][2] else ' '}] {options_n[5][1]}"))
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
        elif choice == "1":
            clear_screen()
            options_n[0] = (options_n[0][0], options_n[0][1], not options_n[0][2])
        elif choice == "2":
            clear_screen()
            options_n[1] = (options_n[1][0], options_n[1][1], not options_n[1][2])
        elif choice == "3":
            clear_screen()
            options_n[2] = (options_n[2][0], options_n[2][1], not options_n[2][2])
        elif choice == "4":
            clear_screen()
            options_n[3] = (options_n[3][0], options_n[3][1], not options_n[3][2])
        elif choice == "5":
            clear_screen()
            options_n[4] = (options_n[4][0], options_n[4][1], not options_n[4][2])
        elif choice == "6":
            clear_screen()
            options_n[5] = (options_n[5][0], options_n[5][1], not options_n[5][2])
        elif choice == "":
            clear_screen()
            active_ns: List[str] = [n_key for _, n_key, active in options_n if active]
            if not active_ns:
                print("Selecione o 1, 2, 3, 4, 5 ou 6 para validar os dados.")
                print()
                input("Digite qualquer tecla para voltar ao menu.")
                continue
            ran_any = False
            if "n1" in active_ns:
                validate_n1("dataset.json", "predicts", "metrics/validate_n1.json")
                ran_any = True
            if "n2" in active_ns:
                validate_n2("dataset.json", "predicts", "metrics/validate_n2.json")
                ran_any = True
            if not ran_any:
                print("Validacao ainda nao implementada.")
            wait_to_return()
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()
