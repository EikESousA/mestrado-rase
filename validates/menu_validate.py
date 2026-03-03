import shutil
from pathlib import Path
from typing import List, Tuple

from utils.app.test_mode_dataset import ensure_test_dataset
from utils.generates.model_registry import MODEL_NAMES
from validates.validate_n1 import validate_n1
from validates.validate_n2 import validate_n2
from validates.validate_n3 import validate_n3
from validates.validate_n1n2 import validate_n1n2
from validates.validate_n1n2n3 import validate_n1n2n3
from utils.screens.clear_screen import clear_screen
from utils.screens.menu_bar_line import menu_bar_line
from utils.screens.menu_prompt import menu_prompt
from utils.screens.menu_text_line import menu_text_line
from utils.screens.read_single_key import read_single_key
from utils.screens.show_debug_banner import show_debug_banner
from utils.screens.wait_to_return import wait_to_return

PREDICT_PREFIXES: List[str] = [
    "generate_n1",
    "generate_n2",
    "generate_n3",
    "generate_n1n2",
    "generate_n1n2n3",
]


def _prepare_test_predicts_alias(
    predicts_dir: str = "predicts",
    alias_dir: str = "predicts/test_validate_alias",
) -> str:
    source = Path(predicts_dir)
    target = Path(alias_dir)
    target.mkdir(parents=True, exist_ok=True)

    for old_file in target.glob("*.json"):
        old_file.unlink()

    copied = 0
    for prefix in PREDICT_PREFIXES:
        for model in MODEL_NAMES:
            src_file = source / f"{prefix}_{model}_test.json"
            dst_file = target / f"{prefix}_{model}.json"
            if src_file.exists():
                shutil.copyfile(src_file, dst_file)
                copied += 1

    if copied == 0:
        print("Nenhum arquivo *_test foi encontrado em predicts/.")
    return str(target)


def menu_validate() -> None:
    options_n: List[Tuple[str, str, bool]] = [
        ("1", "n1", True),
        ("2", "n2", False),
        ("3", "n3", False),
        ("4", "n1n2", False),
        ("5", "n1n2n3", False),
    ]
    option_test: Tuple[str, str, bool] = ("t", "teste (le arquivos *_test)", False)

    while True:
        show_debug_banner()
        print(menu_bar_line())
        print(menu_text_line("VALIDAR DADOS", align_left=False))
        print(menu_bar_line())
        print(
            menu_text_line(
                "Metricas: exact_match, fuzzywuzzy, tfidf, sbert, bertimbau, multilingual, wmd_ft, wmd_nilc"
            )
        )
        print(menu_bar_line())
        print(menu_text_line(f"1 - [{'x' if options_n[0][2] else ' '}] {options_n[0][1]}"))
        print(menu_text_line(f"2 - [{'x' if options_n[1][2] else ' '}] {options_n[1][1]}"))
        print(menu_text_line(f"3 - [{'x' if options_n[2][2] else ' '}] {options_n[2][1]}"))
        print(menu_text_line(f"4 - [{'x' if options_n[3][2] else ' '}] {options_n[3][1]}"))
        print(menu_text_line(f"5 - [{'x' if options_n[4][2] else ' '}] {options_n[4][1]}"))
        print(menu_bar_line())
        print(menu_text_line(f"t - [{'x' if option_test[2] else ' '}] {option_test[1]}"))
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
        elif choice == "t":
            clear_screen()
            option_test = (option_test[0], option_test[1], not option_test[2])
        elif choice == "":
            clear_screen()
            active_ns: List[str] = [n_key for _, n_key, active in options_n if active]
            test_mode = option_test[2]
            if not active_ns:
                print("Selecione o 1, 2, 3, 4 ou 5 para validar os dados.")
                print()
                input("Digite qualquer tecla para voltar ao menu.")
                continue

            dataset_path = "dataset.json"
            predicts_path = "predicts"
            metrics_suffix = ""
            if test_mode:
                dataset_path = ensure_test_dataset(
                    dataset_path="dataset.json",
                    output_path="predicts/dataset_test.json",
                    limit=5,
                )
                predicts_path = _prepare_test_predicts_alias()
                metrics_suffix = "_test"

            ran_any = False
            if "n1n2" in active_ns:
                validate_n1n2(
                    dataset_path,
                    predicts_path,
                    f"metrics/validate_n1n2{metrics_suffix}.json",
                    output_n1=f"metrics/validate_n1_from_n1n2{metrics_suffix}.json",
                    output_n2=f"metrics/validate_n2_from_n1n2{metrics_suffix}.json",
                )
                ran_any = True
            if "n1n2n3" in active_ns:
                validate_n1n2n3(
                    dataset_path,
                    predicts_path,
                    f"metrics/validate_n1n2n3{metrics_suffix}.json",
                    output_n1=f"metrics/validate_n1_from_n1n2n3{metrics_suffix}.json",
                    output_n2=f"metrics/validate_n2_from_n1n2n3{metrics_suffix}.json",
                    output_n3=f"metrics/validate_n3_from_n1n2n3{metrics_suffix}.json",
                )
                ran_any = True
            if "n1" in active_ns and "n1n2" not in active_ns and "n1n2n3" not in active_ns:
                validate_n1(
                    dataset_path,
                    predicts_path,
                    f"metrics/validate_n1{metrics_suffix}.json",
                )
                ran_any = True
            if (
                "n2" in active_ns
                and "n1n2" not in active_ns
                and "n1n2n3" not in active_ns
            ):
                validate_n2(
                    dataset_path,
                    predicts_path,
                    f"metrics/validate_n2{metrics_suffix}.json",
                )
                ran_any = True
            if (
                "n3" in active_ns
                and "n1n2" not in active_ns
                and "n1n2n3" not in active_ns
            ):
                validate_n3(
                    dataset_path,
                    predicts_path,
                    f"metrics/validate_n3{metrics_suffix}.json",
                )
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
