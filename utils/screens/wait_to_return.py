from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_text_line import menu_text_line


def wait_to_return() -> None:
    print(menu_bar_line())
    print(menu_text_line("Digite qualquer tecla para voltar ao menu."))
    print(menu_bar_line())
    input()
