import argparse
import os

from generates.menu_generate import menu_generate
from utils.app._bootstrap_venv import _bootstrap_venv
from utils.screens.clear_screen import clear_screen
from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_prompt import menu_prompt
from utils.screens.menu_text_line import menu_text_line
from utils.screens.read_single_key import read_single_key
from utils.screens.show_debug_banner import show_debug_banner
from validates.menu_validate import menu_validate


def main() -> None:
    parser = argparse.ArgumentParser(description="Menu de geracao e validacao.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilita log detalhado nas geracoes.",
    )
    args: argparse.Namespace = parser.parse_args()

    if args.debug:
        os.environ["GENERATE_DEBUG"] = "1"

    try:
        while True:
            clear_screen()
            show_debug_banner()
            print(menu_bar_line())
            print(menu_text_line("Universidade Federal de Sergipe", align_left=False, color="yellow"))
            print(menu_bar_line())
            print(menu_text_line("Eike Natan Sousa Brito", align_left=False, color="yellow"))
            print(menu_bar_line())
            print(menu_text_line("1 - Gerar dados", align_left=True))
            print(menu_text_line("2 - Validar Dados", align_left=True))
            print(menu_bar_line())
            print(menu_text_line("0 - Sair", align_left=True, color="red"))
            print(menu_bar_line())
            menu_prompt("Escolha uma opcao: ", color="green")
            print(menu_bar_line())

            choice: str = read_single_key().strip()
            print()

            if choice == "1":
                clear_screen()
                menu_generate()
                print()
            elif choice == "2":
                clear_screen()
                menu_validate()
                print()
            elif choice == "0":
                clear_screen()
                print(menu_bar_line())
                print(menu_text_line("Programa encerrado", align_left=False, color="red"))
                print(menu_bar_line())
                break
            else:
                clear_screen()
                print("Digite uma das opcoes")
                print()
    except KeyboardInterrupt:
        print(menu_bar_line())
        print(menu_text_line("Programa encerrado", align_left=False, color="red"))
        print(menu_bar_line())


if __name__ == "__main__":
    _bootstrap_venv()
    main()
