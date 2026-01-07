import os

from generates.menu_generate import show_generated_data
from menu_validate import show_validated_data


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    while True:
        clear_screen()
        print("1 - Gerar dados")
        print("2 - Validar Dados")
        print()
        print("0 - Sair")
        print()
        print("Escolha uma opcao: ", end="")

        choice = input().strip()

        if choice == "1":
            clear_screen()
            show_generated_data()
            print()
        elif choice == "2":
            clear_screen()
            show_validated_data()
            print()
        elif choice == "0":
            print("Programa encerrado.")
            break
        else:
            clear_screen()
            print("Digite uma das opcoes")
            print()


if __name__ == "__main__":
    main()
