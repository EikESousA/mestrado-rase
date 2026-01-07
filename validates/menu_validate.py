from validates.validate_n1 import validate_n1
from utils.screen_utils import (
    clear_screen,
    menu_bar_line,
    menu_prompt,
    menu_text_line,
    read_single_key,
    show_debug_banner,
)


def show_validated_data() -> None:
    options_n = [
        ("1", "n1", False),
        ("2", "n2", True),
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

        choice = read_single_key().strip()
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
            validate_data(options_n)
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()


def validate_data(ns) -> None:
    active_ns = [n_key for _, n_key, active in ns if active]

    if not active_ns:
        print("Selecione o 1, 2, 3, 4, 5 ou 6 para validar os dados.")
        print()
        input("Digite qualquer tecla para voltar ao menu.")
        return

    if "n1" in active_ns:
        validate_n1("dataset.json", "predicts", "metrics/validate_n1.json")
        print()
        input("Digite qualquer tecla para voltar ao menu.")
        return

    print("Validacao ainda nao implementada.")
    print()
    input("Digite qualquer tecla para voltar ao menu.")
