import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path


def _in_venv() -> bool:
    return sys.prefix != sys.base_prefix


def _requirements_hash(req_path: Path) -> str:
    return hashlib.sha256(req_path.read_bytes()).hexdigest()


def _ensure_venv() -> Path:
    root = Path(__file__).resolve().parent
    venv_dir = root / ".venv"
    python_bin = venv_dir / "bin" / "python"
    req_file = root / "requirements.txt"
    stamp_file = venv_dir / ".requirements.sha256"

    if not venv_dir.exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])

    if req_file.exists():
        current_hash = _requirements_hash(req_file)
        previous_hash = stamp_file.read_text().strip() if stamp_file.exists() else ""
        if current_hash != previous_hash:
            subprocess.check_call(
                [str(python_bin), "-m", "pip", "install", "-r", str(req_file)]
            )
            stamp_file.write_text(current_hash + "\n")

    return python_bin


def _bootstrap_venv() -> None:
    if _in_venv():
        return
    python_bin = _ensure_venv()
    os.execv(str(python_bin), [str(python_bin)] + sys.argv)


def main():
    parser = argparse.ArgumentParser(description="Menu de geracao e validacao.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Habilita log detalhado nas geracoes.",
    )
    args = parser.parse_args()

    if args.debug:
        os.environ["GENERATE_DEBUG"] = "1"

    from generates.menu_generate import show_generated_data
    from menu_validate import show_validated_data
    from utils.screen_utils import (
        clear_screen,
        MENU_WIDTH,
        menu_bar_line,
        menu_prompt,
        menu_text_line,
        read_single_key,
    )

    try:
        while True:
            clear_screen()
            print(menu_bar_line(MENU_WIDTH))
            print(menu_text_line("Universidade Federal de Sergipe", MENU_WIDTH, align_left=False, color="yellow"))
            print(menu_bar_line(MENU_WIDTH))
            print(menu_text_line("Eike Natan Sousa Brito", MENU_WIDTH, align_left=False, color="yellow"))
            print(menu_bar_line(MENU_WIDTH))
            print(menu_text_line("1 - Gerar dados", MENU_WIDTH, align_left=True))
            print(menu_text_line("2 - Validar Dados", MENU_WIDTH, align_left=True))
            print(menu_bar_line(MENU_WIDTH))
            print(menu_text_line("0 - Sair", MENU_WIDTH, align_left=True, color="red"))
            print(menu_bar_line(MENU_WIDTH))
            menu_prompt("Escolha uma opcao: ", MENU_WIDTH, color="green")
            print(menu_bar_line(MENU_WIDTH))

            choice = read_single_key().strip()
            print()

            if choice == "1":
                clear_screen()
                show_generated_data()
                print()
            elif choice == "2":
                clear_screen()
                show_validated_data()
                print()
            elif choice == "0":
                clear_screen()
                print(menu_bar_line(MENU_WIDTH))
                print(menu_text_line("Programa encerrado", MENU_WIDTH, align_left=False, color="red"))
                print(menu_bar_line(MENU_WIDTH))
                break
            else:
                clear_screen()
                print("Digite uma das opcoes")
                print()
    except KeyboardInterrupt:
        clear_screen()
        print(menu_bar_line(MENU_WIDTH))
        print(menu_text_line("Programa encerrado", MENU_WIDTH, align_left=False, color="red"))
        print(menu_bar_line(MENU_WIDTH))


if __name__ == "__main__":
    _bootstrap_venv()
    main()
