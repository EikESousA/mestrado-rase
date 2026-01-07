from utils.generates.run_generator import run_generator
from utils.screens.clear_screen import clear_screen
from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_prompt import menu_prompt
from utils.screens.menu_text_line import menu_text_line
from utils.screens.read_single_key import read_single_key
from utils.screens.show_debug_banner import show_debug_banner
from utils.screens.wait_to_return import wait_to_return


def menu_generate() -> None:
    options_n = [
        ("1", "n1", False),
        ("2", "n2", True),
        ("3", "n3", False),
        ("4", "n1_n2", False),
        ("5", "n2_n3", False),
        ("6", "n1_n2_n3", False),
    ]
    options_model = [
        ("a", "alpaca", True),
        ("b", "dolphin", False),
        ("c", "llama", False),
        ("d", "mistral", False),
        ("e", "gemma", False),
        ("f", "qwen", False),
    ]

    while True:
        show_debug_banner()
        print(menu_bar_line())
        print(menu_text_line("GERAR DADOS", align_left=False))
        print(menu_bar_line())
        print(menu_text_line(f"1 - [{'x' if options_n[0][2] else ' '}] {options_n[0][1]}"))
        print(menu_text_line(f"2 - [{'x' if options_n[1][2] else ' '}] {options_n[1][1]}"))
        print(menu_text_line(f"3 - [{'x' if options_n[2][2] else ' '}] {options_n[2][1]}"))
        print(menu_text_line(f"4 - [{'x' if options_n[3][2] else ' '}] {options_n[3][1]}"))
        print(menu_text_line(f"5 - [{'x' if options_n[4][2] else ' '}] {options_n[4][1]}"))
        print(menu_text_line(f"6 - [{'x' if options_n[5][2] else ' '}] {options_n[5][1]}"))
        print(menu_bar_line())
        print(menu_text_line(f"a - [{'x' if options_model[0][2] else ' '}] {options_model[0][1]}"))
        print(menu_text_line(f"b - [{'x' if options_model[1][2] else ' '}] {options_model[1][1]}"))
        print(menu_text_line(f"c - [{'x' if options_model[2][2] else ' '}] {options_model[2][1]}"))
        print(menu_text_line(f"d - [{'x' if options_model[3][2] else ' '}] {options_model[3][1]}"))
        print(menu_text_line(f"e - [{'x' if options_model[4][2] else ' '}] {options_model[4][1]}"))
        print(menu_text_line(f"f - [{'x' if options_model[5][2] else ' '}] {options_model[5][1]}"))
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
        elif choice == "a":
            clear_screen()
            options_model[0] = (options_model[0][0], options_model[0][1], not options_model[0][2])
        elif choice == "b":
            clear_screen()
            options_model[1] = (options_model[1][0], options_model[1][1], not options_model[1][2])
        elif choice == "c":
            clear_screen()
            options_model[2] = (options_model[2][0], options_model[2][1], not options_model[2][2])
        elif choice == "d":
            clear_screen()
            options_model[3] = (options_model[3][0], options_model[3][1], not options_model[3][2])
        elif choice == "e":
            clear_screen()
            options_model[4] = (options_model[4][0], options_model[4][1], not options_model[4][2])
        elif choice == "f":
            clear_screen()
            options_model[5] = (options_model[5][0], options_model[5][1], not options_model[5][2])
        elif choice == "":
            clear_screen()
            active_ns = [n_key for _, n_key, active in options_n if active]
            active_models = [model_key for _, model_key, active in options_model if active]

            if not active_ns:
                print("Selecione o 1, 2, 3, 4, 5 ou 6 para gerar os dados.")
                print()
                input("Digite qualquer tecla para voltar ao menu.")
                continue

            if not active_models:
                print("Selecione um modelo para gerar os dados.")
                print()
                input("Digite qualquer tecla para voltar ao menu.")
                continue

            for n_key in active_ns:
                run_generator(n_key, active_models)

            wait_to_return()
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()
