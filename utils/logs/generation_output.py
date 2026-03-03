from typing import Callable


SEPARATOR = "-----------------------------------------------------------------"


def _normalize_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def _emit(message: str, log: Callable[[str], None] | None = None) -> None:
    print(message)
    if log is not None:
        log(message)


def _blank(log: Callable[[str], None] | None = None, count: int = 1) -> None:
    for _ in range(count):
        print()
        if log is not None:
            log("")


def print_generation_start(
    stage_label: str,
    model_name: str,
    input_path: str,
    log: Callable[[str], None] | None = None,
) -> None:
    _blank(log, 0)
    _emit(f"Gerando {stage_label} com modelo {model_name}", log)
    _blank(log, 0)
    _emit(f"Lendo arquivo {input_path}", log)
    _blank(log, 1)


def print_text_progress(
    text_index: int,
    elapsed_time: float,
    text: str,
    log: Callable[[str], None] | None = None,
    status_marker: str = "",
) -> None:
    prefix = f"{status_marker} " if status_marker else ""
    message = f"{prefix}Text {text_index} ({elapsed_time:.2f}s): {_normalize_text(text)}"
    _emit(message, log)
    _blank(log, 1)


def print_generation_end(
    elapsed_time: float,
    output_path: str,
    log: Callable[[str], None] | None = None,
) -> None:
    _blank(log, 1)
    _emit(
        f"Processamento concluido. Tempo de processamento {elapsed_time:.2f} segundos.",
        log,
    )
    _blank(log, 0)
    _emit(f"Resultado salvo em {output_path}", log)
    _blank(log, 0)
    _emit(SEPARATOR, log)


def print_generation_aborted(
    elapsed_time: float,
    output_path: str,
    log: Callable[[str], None] | None = None,
) -> None:
    _blank(log, 1)
    _emit(
        f"Processamento interrompido. Tempo de processamento {elapsed_time:.2f} segundos.",
        log,
    )
    _blank(log, 0)
    _emit(f"Resultado parcial salvo em {output_path}", log)
    _blank(log, 0)
    _emit(SEPARATOR, log)
