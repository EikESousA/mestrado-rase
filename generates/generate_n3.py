import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_ollama import OllamaLLM

from utils.generates.build_ollama_llm_kwargs import build_ollama_llm_kwargs
from utils.generates.generate_config import generate_config
from utils.generates.model_registry import MODEL_NAMES
from utils.generates.model_runtime_error import FatalModelRuntimeError
from utils.generates.resolve_display_input_path import resolve_display_input_path
from utils.logs.generation_output import (
    print_generation_aborted,
    print_generation_end,
    print_generation_start,
    print_text_progress,
)
from utils.logs.init_log import init_log
from utils.n3.build_chains import build_chains
from utils.n3.build_context import build_context
from utils.n3.constants import PROMPT_INPUT_KEYS
from utils.n3.empty_operator import empty_operator
from utils.n3.extract_properties import extract_properties
from utils.n3.is_debug_enabled import is_debug_enabled
from utils.n3.load_templates import load_templates
from utils.n3.string_value import string_value


def generate_n3(
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
    stage_label: str = "N3",
    model_name: str | None = None,
) -> None:
    if input_path is None or output_path is None or model_id is None:
        parser = argparse.ArgumentParser(description="Gerar propriedades RASE N3.")
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

        input_path, output_path, model_id = generate_config("n3", args.model)
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

    templates = load_templates()
    if templates is None:
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
    chains = build_chains(llm, templates)

    result_data: Dict[str, Any] = {"counts": 0, "datas": [], "time": 0.0}
    total_start_time: float = time.time()
    debug_enabled: bool = is_debug_enabled()
    aborted = False

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, ensure_ascii=False, indent=2)

    print_generation_start(stage_label, model_name, resolve_display_input_path(input_path), log)

    try:
        for text_index, item in enumerate(data.get("datas", [])):
            count = text_index + 1
            full_text = string_value(item.get("text", ""))
            start_time: float = time.time()

            text_context = build_context(text_index)
            log(f"{text_context} Iniciando Texto {count}")
            texts_n1: list[Dict[str, Any]] = []
            abort_model = False

            for sentence_index, n1_item in enumerate(item.get("texts_n1", [])):
                n1_index = sentence_index + 1
                text_n1 = string_value(n1_item.get("text_n1", ""))
                sentence_context = build_context(text_index, sentence_index)
                sentence_preview = text_n1.replace("\n", " ").strip()[:60]
                sentence_suffix = "..." if len(text_n1.strip()) > 60 else ""
                log(
                    f"{sentence_context} Iniciando sentenca {n1_index}: "
                    f"{sentence_preview}{sentence_suffix}"
                )
                operators_n2_raw = n1_item.get("operators_n2", {})
                if not isinstance(operators_n2_raw, dict):
                    operators_n2_raw = {}

                operators_n2: Dict[str, Dict[str, Any]] = {}
                for op_key in PROMPT_INPUT_KEYS:
                    operator = empty_operator(operators_n2_raw.get(op_key, {}))
                    text_n2 = operator["text_n2"]
                    if not text_n2:
                        log(
                            f"{build_context(text_index, sentence_index, op_key)} "
                            "Operador vazio, mantendo properties_n3 vazio."
                        )
                        operators_n2[op_key] = operator
                        continue

                    try:
                        operator["properties_n3"] = extract_properties(
                            op_key=op_key,
                            text_n2=text_n2,
                            full_text=full_text,
                            text_n1=text_n1,
                            chains=chains,
                            model_id=model_id,
                            count_display=count,
                            n1_display=n1_index,
                            text_index=text_index,
                            sentence_index=sentence_index,
                            debug_enabled=debug_enabled,
                            strict_json=strict_json,
                            log=log,
                        )
                    except FatalModelRuntimeError as exc:
                        print(str(exc))
                        log(f"{build_context(text_index, sentence_index, op_key)} {exc}")
                        abort_model = True
                        break
                    operators_n2[op_key] = operator

                if abort_model:
                    aborted = True
                    break

                texts_n1.append(
                    {
                        "text_n1": text_n1,
                        "operators_n2": operators_n2,
                    }
                )

            if abort_model:
                result_data["time"] = time.time() - total_start_time
                break

            elapsed_time: float = time.time() - start_time
            result_entry: Dict[str, Any] = {
                "text": full_text,
                "texts_n1": texts_n1,
            }

            result_data["datas"].append(result_entry)
            result_data["counts"] = count
            result_data["time"] = time.time() - total_start_time

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, ensure_ascii=False, indent=2)

            print_text_progress(count, elapsed_time, full_text, log)
            log(f"{text_context} Texto {count} concluido ({elapsed_time:.2f}s)")
        result_data["time"] = time.time() - total_start_time
        if aborted:
            print_generation_aborted(result_data["time"], output_path, log)
            return

        print_generation_end(result_data["time"], output_path, log)
    finally:
        close_log()


if __name__ == "__main__":
    generate_n3()
