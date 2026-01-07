from utils.generate_utils import get_active_names, run_generator, wait_to_return
from utils.screen import clear_screen

def show_generated_data():
    options_n = [
        ("n1", True),
        ("n2", False),
        ("n3", False),
    ]
    options_model = [
        ("alpaca", False),
        ("dolphin", False),
        ("llama", False),
        ("mistral", True),
    ]

    while True:
        print("1 - [{}] {}".format("x" if options_n[0][1] else " ", options_n[0][0]))
        print("2 - [{}] {}".format("x" if options_n[1][1] else " ", options_n[1][0]))
        print("3 - [{}] {}".format("x" if options_n[2][1] else " ", options_n[2][0]))
        print()
        print("4 - [{}] {}".format("x" if options_model[0][1] else " ", options_model[0][0]))
        print("5 - [{}] {}".format("x" if options_model[1][1] else " ", options_model[1][0]))
        print("6 - [{}] {}".format("x" if options_model[2][1] else " ", options_model[2][0]))
        print("7 - [{}] {}".format("x" if options_model[3][1] else " ", options_model[3][0]))
        print()
        print("8 - Processar")
        print()
        print("0 - Voltar")
        print()
        print("Escolha uma opcao: ", end="")

        choice = input().strip()

        if choice == "0":
            clear_screen()
            break
        elif choice == "1":
            clear_screen()
            options_n[0] = (options_n[0][0], not options_n[0][1])
        elif choice == "2":
            clear_screen()
            options_n[1] = (options_n[1][0], not options_n[1][1])
        elif choice == "3":
            clear_screen()
            options_n[2] = (options_n[2][0], not options_n[2][1])
        elif choice == "4":
            clear_screen()
            options_model[0] = (options_model[0][0], not options_model[0][1])
        elif choice == "5":
            clear_screen()
            options_model[1] = (options_model[1][0], not options_model[1][1])
        elif choice == "6":
            clear_screen()
            options_model[2] = (options_model[2][0], not options_model[2][1])
        elif choice == "7":
            clear_screen()
            options_model[3] = (options_model[3][0], not options_model[3][1])
        elif choice == "8":
            clear_screen()
            generate_data(options_n, options_model)
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()

def generate_data(ns, models):
    active_ns = get_active_names(ns)
    active_models = get_active_names(models)

    if not active_ns:
        print("Selecione o N1, N2 ou N3 para gerar os dados.")
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
