import os

from generate import generate_data


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_generated_data():
    options_n = [
        ("n1", False),
        ("n2", False),
        ("n3", False),
    ]
    options_model = [
        ("alpaca", False),
        ("dolphin", False),
        ("llama", False),
    ]

    while True:
        print("1 - [{}] {}".format("x" if options_n[0][1] else " ", options_n[0][0]))
        print("2 - [{}] {}".format("x" if options_n[1][1] else " ", options_n[1][0]))
        print("3 - [{}] {}".format("x" if options_n[2][1] else " ", options_n[2][0]))
        print()
        print("4 - [{}] {}".format("x" if options_model[0][1] else " ", options_model[0][0]))
        print("5 - [{}] {}".format("x" if options_model[1][1] else " ", options_model[1][0]))
        print("6 - [{}] {}".format("x" if options_model[2][1] else " ", options_model[2][0]))
        print()
        print("7 - Processar")
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
            generate_data(options_n, options_model)
            clear_screen()
            print()
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()
