import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import OllamaLLM

from utils.generates.build_ollama_llm_kwargs import build_ollama_llm_kwargs
from utils.generates.generate_config import generate_config
from utils.generates.invoke_with_timeout import invoke_with_timeout
from utils.generates.model_registry import MODEL_NAMES
from utils.generates.model_runtime_error import (
    build_fatal_model_runtime_message,
    is_fatal_model_runtime_error,
)
from utils.generates.reset_model import reset_model
from utils.generates.resolve_display_input_path import resolve_display_input_path
from utils.logs.generation_output import (
    print_generation_aborted,
    print_generation_end,
    print_generation_start,
    print_text_progress,
)
from utils.logs.init_log import init_log
from utils.n1.normalize_sentence import normalize_sentence
from utils.n2.build_context import build_context
from utils.n2.build_operators import build_operators
from utils.n2.constants import PROMPT_PATH
from utils.n2.is_valid_json_object import is_valid_json_object
from utils.n2.process_text import process_text
from utils.n2.validate_n2_result import validate_n2_result


def generate_n2(
    input_path: str | None = None,
    output_path: str | None = None,
    model_id: str | None = None,
    log_path: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
    repeat_penalty: float | None = None,
    seed: int | None = None,
    num_ctx: int | None = None,
    num_predict: int | None = None,
    strict_json: bool = False,
    use_json_format: bool = True,
    stage_label: str = "N2",
    model_name: str | None = None,
) -> None:
    def is_invalid_n1_sentence(value: str) -> bool:
        return not value or not re.search(r"[A-Za-zÀ-ÿ]", value)

    if input_path is None or output_path is None or model_id is None:
        parser = argparse.ArgumentParser(description="Gerar operadores RASE N2.")
        parser.add_argument(
            "--model",
            choices=MODEL_NAMES,
            default="mistral",
            help="Modelo base para geracao.",
        )
        parser.add_argument("--input", dest="input_path", default=None)
        parser.add_argument("--output", dest="output_path", default=None)
        parser.add_argument("--log", dest="log_path", default=None)
        parser.add_argument("--temperature", type=float, default=0.1)
        parser.add_argument("--top-p", dest="top_p", type=float, default=0.9)
        parser.add_argument("--top-k", dest="top_k", type=int, default=40)
        parser.add_argument("--repeat-penalty", dest="repeat_penalty", type=float, default=1.1)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument("--num-ctx", dest="num_ctx", type=int, default=None)
        parser.add_argument("--num-predict", dest="num_predict", type=int, default=None)
        parser.add_argument("--strict-json", action="store_true")
        parser.add_argument("--no-json-format", action="store_true")
        args: argparse.Namespace = parser.parse_args()

        input_path, output_path, model_id = generate_config("n2", args.model)
        input_path = str(input_path)
        output_path = str(output_path)
        model_id = str(model_id)
        if args.output_path:
            output_path = args.output_path
        log_path = args.log_path
        temperature = args.temperature
        top_p = args.top_p
        top_k = args.top_k
        repeat_penalty = args.repeat_penalty
        seed = args.seed
        num_ctx = args.num_ctx
        num_predict = args.num_predict
        strict_json = args.strict_json
        use_json_format = not args.no_json_format
        model_name = args.model

    if input_path is None or output_path is None or model_id is None:
        print("Erro: parametros obrigatorios nao encontrados.")
        return
    if model_name is None:
        model_name = model_id

    if temperature is None:
        temperature = 0.1
    if top_p is None:
        top_p = 0.9
    if top_k is None:
        top_k = 40
    if repeat_penalty is None:
        repeat_penalty = 1.1
    if seed is None:
        seed = 42

    try:
        template: str = PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("Erro: prompt n2 nao encontrado em prompts/n2.txt.")
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    data: Dict[str, Any] = {}
    log: Callable[[str], None]
    close_log: Callable[[], None]
    log, close_log = init_log(output_path, log_path)

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Erro: Arquivo de entrada nao encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro: Falha ao decodificar JSON de entrada.")
        return

    llm_kwargs: Dict[str, Any] = build_ollama_llm_kwargs(
        model=model_id,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        repeat_penalty=repeat_penalty,
        seed=seed,
        num_ctx=num_ctx,
        num_predict=num_predict,
        use_json_format=use_json_format,
    )

    llm: OllamaLLM = OllamaLLM(**llm_kwargs)
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
    chain: RunnableSerializable[Dict[str, str], str] = prompt | llm

    result_data: Dict[str, Any] = {"counts": 0, "datas": [], "time": 0.0}
    total_start_time: float = time.time()
    aborted = False

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, ensure_ascii=False, indent=2)

    print_generation_start(stage_label, model_name, resolve_display_input_path(input_path), log)

    try:
        for text_index, item in enumerate(data["datas"]):
            count = text_index + 1
            start_time: float = time.time()

            text_context = build_context(text_index)
            log(f"{text_context} Iniciando Texto {count}")
            texts_n1: List[Dict[str, Any]] = []
            abort_model = False
            text_has_failure = False
            for sentence_index, n1_item in enumerate(item.get("texts_n1", [])):
                n1_index = sentence_index + 1
                text_n1 = normalize_sentence(str(n1_item.get("text_n1", "")))
                processed_result: Dict[str, str] = {}
                valid_result = False
                context = build_context(text_index, sentence_index)

                if is_invalid_n1_sentence(text_n1):
                    msg = (
                        "Sentenca N1 invalida ou vazia; "
                        "mantendo operadores vazios."
                    )
                    print(
                        f"{msg} (texto {count}, sentenca {n1_index})."
                    )
                    log(f"{context} {msg}")
                    text_has_failure = True
                    texts_n1.append(
                        {
                            "text_n1": "",
                            "operators_n2": build_operators({}),
                        }
                    )
                    continue

                for attempt in range(1, 4):
                    log(
                        f"{context} Chamando modelo "
                        f"(texto {count}, sentenca {n1_index}, tentativa {attempt})"
                    )
                    try:
                        result: str | None
                        timed_out: bool
                        result, timed_out = invoke_with_timeout(
                            chain,
                            {"text": item["text"], "text_n1": text_n1},
                            600.0,
                            60.0,
                            log,
                        )
                        if timed_out:
                            msg = (
                                "Timeout na chamada do modelo "
                                f"apos {int(600.0)}s."
                            )
                            print(msg)
                            log(f"{context} {msg}")
                            reset_model(model_id, log)
                            continue
                        if result is None:
                            raise RuntimeError("Resposta vazia do modelo.")
                    except Exception as exc:
                        print(
                            "Erro na chamada do modelo "
                            f"(texto {count}, sentenca {n1_index}, "
                            f"tentativa {attempt}): {exc}"
                        )
                        log(
                            f"{context} Erro na chamada do modelo "
                            f"(texto {count}, sentenca {n1_index}, "
                            f"tentativa {attempt}): {exc}"
                        )
                        if is_fatal_model_runtime_error(exc):
                            msg = build_fatal_model_runtime_message(model_id, exc)
                            print(msg)
                            log(f"{context} {msg}")
                            abort_model = True
                            break
                        if attempt < 3:
                            time.sleep(1)
                        continue

                    log(f"{context} Saida do modelo:\n{result}")
                    env_debug = os.getenv("GENERATE_DEBUG", "").strip().lower()
                    if env_debug in {"1", "true", "yes", "on"}:
                        print("Saida do modelo:")
                        print(result)

                    if strict_json and not is_valid_json_object(result):
                        log(
                            f"{context} Saida invalida para strict-json "
                            f"(texto {count}, sentenca {n1_index}, tentativa {attempt})"
                        )
                        continue

                    processed_result = process_text(result)
                    valid_result, reason = validate_n2_result(processed_result)
                    if valid_result:
                        break
                    log(
                        f"{context} Saida invalida para N2 "
                        f"(texto {count}, sentenca {n1_index}, tentativa {attempt}): {reason}"
                    )

                if abort_model:
                    aborted = True
                    break

                if not valid_result:
                    log(
                        f"{context} Falha ao processar texto "
                        f"(texto {count}, sentenca {n1_index})."
                    )
                    text_has_failure = True
                    processed_result = {}

                operators_n2 = build_operators(processed_result)
                texts_n1.append(
                    {
                        "text_n1": text_n1,
                        "operators_n2": operators_n2,
                    }
                )

            if abort_model:
                result_data["time"] = time.time() - total_start_time
                break

            end_time: float = time.time()
            elapsed_time: float = end_time - start_time

            result_entry: Dict[str, Any] = {
                "text": item["text"],
                "texts_n1": texts_n1,
            }

            result_data["datas"].append(result_entry)
            result_data["counts"] = count
            result_data["time"] = time.time() - total_start_time

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, ensure_ascii=False, indent=2)

            if text_has_failure:
                print_text_progress(count, elapsed_time, item["text"], log, "[X]")
            else:
                print_text_progress(count, elapsed_time, item["text"], log, "[V]")
            log(f"{text_context} Texto {count} concluido ({elapsed_time:.2f}s)")
        result_data["time"] = time.time() - total_start_time
        if aborted:
            print_generation_aborted(result_data["time"], output_path, log)
            return

        print_generation_end(result_data["time"], output_path, log)
    finally:
        close_log()


if __name__ == "__main__":
    generate_n2()
