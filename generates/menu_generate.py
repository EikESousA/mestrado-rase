from utils.generate_utils import run_generator, wait_to_return
from utils.screen_utils import (
    clear_screen,
    MENU_WIDTH,
    menu_bar_line,
    menu_prompt,
    menu_text_line,
    read_single_key,
    show_debug_banner,
)

def show_generated_data():
    options_n = [
        ("1", "n1", False),
        ("2", "n2", True),
        ("3", "n3", False),
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
        show_debug_banner(MENU_WIDTH)
        print(menu_bar_line(MENU_WIDTH))
        print(menu_text_line("GERAR DADOS", MENU_WIDTH, align_left=False))
        print(menu_bar_line(MENU_WIDTH))
        print(menu_text_line(f"1 - [{'x' if options_n[0][2] else ' '}] {options_n[0][1]}", MENU_WIDTH))
        print(menu_text_line(f"2 - [{'x' if options_n[1][2] else ' '}] {options_n[1][1]}", MENU_WIDTH))
        print(menu_text_line(f"3 - [{'x' if options_n[2][2] else ' '}] {options_n[2][1]}", MENU_WIDTH))
        print(menu_bar_line(MENU_WIDTH))
        print(menu_text_line(f"a - [{'x' if options_model[0][2] else ' '}] {options_model[0][1]}", MENU_WIDTH))
        print(menu_text_line(f"b - [{'x' if options_model[1][2] else ' '}] {options_model[1][1]}", MENU_WIDTH))
        print(menu_text_line(f"c - [{'x' if options_model[2][2] else ' '}] {options_model[2][1]}", MENU_WIDTH))
        print(menu_text_line(f"d - [{'x' if options_model[3][2] else ' '}] {options_model[3][1]}", MENU_WIDTH))
        print(menu_text_line(f"e - [{'x' if options_model[4][2] else ' '}] {options_model[4][1]}", MENU_WIDTH))
        print(menu_text_line(f"f - [{'x' if options_model[5][2] else ' '}] {options_model[5][1]}", MENU_WIDTH))
        print(menu_bar_line(MENU_WIDTH))
        print(menu_text_line("Enter - Processar", MENU_WIDTH))
        print(menu_bar_line(MENU_WIDTH))
        print(menu_text_line("0 - Voltar", MENU_WIDTH, color="red"))
        print(menu_bar_line(MENU_WIDTH))
        menu_prompt("Escolha uma opcao: ", MENU_WIDTH, color="green")
        print(menu_bar_line(MENU_WIDTH))

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
        elif choice == "g":
            clear_screen()
            options_model[6] = (options_model[6][0], options_model[6][1], not options_model[6][2])
        elif choice == "":
            clear_screen()
            generate_data(options_n, options_model)
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()

def generate_data(ns, models):
    active_ns = [n_key for _, n_key, active in ns if active]
    active_models = [model_key for _, model_key, active in models if active]

    if not active_ns:
        print("Selecione o 1, 2 ou 3 para gerar os dados.")
        print()
        input("Digite qualquer tecla para voltar ao menu.")
        return

    if not active_models:
        print("Selecione um modelo para gerar os dados.")
        print()
        input("Digite qualquer tecla para voltar ao menu.")
        return

    for n_key in active_ns:
        run_generator(n_key, active_models)

    wait_to_return()
