import time
from typing import Callable, Dict

from langchain_core.runnables import RunnableSerializable

from utils.generates.invoke_with_timeout import invoke_with_timeout
from utils.generates.model_runtime_error import (
    FatalModelRuntimeError,
    build_fatal_model_runtime_message,
    is_fatal_model_runtime_error,
)
from utils.generates.reset_model import reset_model
from utils.n2.empty_properties import empty_properties
from utils.n3.build_context import build_context
from utils.n3.constants import PROMPT_INPUT_KEYS, TYPE_BY_OPERATOR
from utils.n3.fallback_properties import fallback_properties
from utils.n3.has_valid_json_object import has_valid_json_object
from utils.n3.parse_properties import try_parse_properties
from utils.n3.validate_properties import validate_and_normalize_properties


def extract_properties(
    op_key: str,
    text_n2: str,
    full_text: str,
    text_n1: str,
    chains: Dict[str, RunnableSerializable[Dict[str, str], str]],
    model_id: str,
    count_display: int,
    n1_display: int,
    text_index: int,
    sentence_index: int,
    debug_enabled: bool,
    strict_json: bool,
    log: Callable[[str], None],
) -> Dict[str, str]:
    expected_type = TYPE_BY_OPERATOR[op_key]
    input_key = PROMPT_INPUT_KEYS[op_key]
    fallback = fallback_properties(op_key, text_n2)
    context = build_context(text_index, sentence_index, op_key)
    if fallback is not None:
        processed, is_valid, reason = validate_and_normalize_properties(
            fallback,
            expected_type=expected_type,
            fill_type_when_missing=False,
        )
        if is_valid:
            log(
                f"{context} Fallback deterministico aplicado (texto {count_display}, sentenca {n1_display}, "
                f"operador {op_key}): {reason}"
            )
            return processed

    processed: Dict[str, str] = empty_properties()

    for attempt in range(1, 4):
        log(
            f"{context} Chamando modelo "
            f"(texto {count_display}, sentenca {n1_display}, "
            f"operador {op_key}, tentativa {attempt})"
        )
        try:
            result: str | None
            timed_out: bool
            result, timed_out = invoke_with_timeout(
                chains[op_key],
                {
                    input_key: text_n2,
                    "text": full_text,
                    "text_n1": text_n1,
                },
                600.0,
                60.0,
                log,
            )
            if timed_out:
                msg = f"Timeout na chamada do modelo apos {int(600.0)}s."
                print(msg)
                log(f"{context} {msg}")
                reset_model(model_id, log)
                continue
            if result is None:
                raise RuntimeError("Resposta vazia do modelo.")
        except Exception as exc:
            print(
                "Erro na chamada do modelo "
                f"(texto {count_display}, sentenca {n1_display}, "
                f"operador {op_key}, tentativa {attempt}): {exc}"
            )
            log(
                f"{context} Erro na chamada do modelo "
                f"(texto {count_display}, sentenca {n1_display}, "
                f"operador {op_key}, tentativa {attempt}): {exc}"
            )
            if is_fatal_model_runtime_error(exc):
                raise FatalModelRuntimeError(
                    build_fatal_model_runtime_message(model_id, exc)
                ) from exc
            if attempt < 3:
                time.sleep(1)
            continue

        log(f"{context} Saida do modelo ({op_key}):\n{result}")
        if debug_enabled:
            print(f"Saida do modelo ({op_key}):")
            print(result)

        if strict_json and not has_valid_json_object(result):
            log(
                f"{context} Resposta invalida para strict-json "
                f"(texto {count_display}, sentenca {n1_display}, operador {op_key})."
            )
            continue

        parsed, parsed_ok = try_parse_properties(result)
        if not parsed_ok:
            log(
                f"{context} JSON nao reconhecido (texto {count_display}, sentenca {n1_display}, "
                f"operador {op_key}, tentativa {attempt})."
            )
            continue

        processed, is_valid, reason = validate_and_normalize_properties(
            parsed,
            expected_type=expected_type,
            fill_type_when_missing=True,
        )
        if is_valid:
            return processed

        log(
            f"{context} Propriedades invalidas (texto {count_display}, sentenca {n1_display}, "
            f"operador {op_key}, tentativa {attempt}): {reason}"
        )

    msg = f"Falha ao processar operador {op_key} (texto {count_display}, sentenca {n1_display})."
    print(msg)
    log(f"{context} {msg}")

    return empty_properties()
