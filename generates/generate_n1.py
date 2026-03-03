import argparse
import json
import os
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
from utils.logs.generation_output import (
    print_generation_aborted,
    print_generation_end,
    print_generation_start,
    print_text_progress,
)
from utils.logs.init_log import init_log
from utils.n1.empty_operators import empty_operators
from utils.n1.process_text import process_text


PROMPT_PATH: Path = Path("prompts") / "n1.txt"


def _ctx(text_index: int) -> str:
    return f"[text_index={text_index}]"


def generate_n1() -> None:
    parser = argparse.ArgumentParser(description="Gerar sentencas RASE N1.")
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
    args: argparse.Namespace = parser.parse_args()

    input_path, output_path, model_id = generate_config("n1", args.model)
    input_path: str = str(input_path)
    output_path: str = str(output_path)
    model_id: str = str(model_id)
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    data: Dict[str, Any] = {}
    log: Callable[[str], None]
    close_log: Callable[[], None]
    log, close_log = init_log(output_path, args.log_path)

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Erro: Arquivo de entrada nao encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro: Falha ao decodificar JSON de entrada.")
        return

    try:
        template: str = PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("Erro: prompt n1 nao encontrado em prompts/n1.txt.")
        return

    llm_kwargs: Dict[str, Any] = build_ollama_llm_kwargs(
        model=model_id,
        temperature=args.temperature,
        top_p=args.top_p,
        top_k=args.top_k,
        repeat_penalty=args.repeat_penalty,
        seed=args.seed,
        num_ctx=args.num_ctx,
        num_predict=args.num_predict,
    )

    llm: OllamaLLM = OllamaLLM(**llm_kwargs)
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
    chain: RunnableSerializable[Dict[str, str], str] = prompt | llm

    result_data: Dict[str, Any] = {"counts": 0, "datas": [], "time": 0.0}
    total_start_time: float = time.time()
    aborted = False

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, ensure_ascii=False, indent=2)

    print_generation_start("N1", args.model, input_path, log)

    try:
        for text_index, item in enumerate(data["datas"]):
            count = text_index + 1
            start_time: float = time.time()
            processed_result: List[str] = []
            abort_model = False

            context = _ctx(text_index)
            log(f"{context} Iniciando Texto {count}")
            for attempt in range(1, 4):
                log(f"{context} Chamando modelo (tentativa {attempt})")
                try:
                    result: str | None
                    timed_out: bool
                    result, timed_out = invoke_with_timeout(
                        chain,
                        {"text": item["text"]},
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
                    print(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    log(f"{context} Erro na chamada do modelo (tentativa {attempt}): {exc}")
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
                processed_result = process_text(result)
                if processed_result:
                    break
                print(f"Tentativa {attempt} retornou vazio. Repetindo.")
                log(f"{context} Tentativa {attempt} retornou vazio. Repetindo.")

            if abort_model:
                aborted = True
                result_data["time"] = time.time() - total_start_time
                break

            end_time: float = time.time()

            elapsed_time: float = end_time - start_time
            if not processed_result:
                msg = (
                    "Falha ao processar texto "
                    "apos 3 tentativas. Seguindo."
                )
                print(msg)
                log(f"{context} {msg}")
            texts_n1: List[Dict[str, Any]] = [
                {"text_n1": sentence, "operators_n2": empty_operators()}
                for sentence in processed_result
            ]
            result_entry: Dict[str, Any] = {"text": item["text"], "texts_n1": texts_n1}

            result_data["datas"].append(result_entry)
            result_data["counts"] = count
            result_data["time"] = time.time() - total_start_time

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, ensure_ascii=False, indent=2)

            print_text_progress(count, elapsed_time, item["text"], log)
            log(f"{context} Texto {count} concluido ({elapsed_time:.2f}s)")
        result_data["time"] = time.time() - total_start_time
        if aborted:
            print_generation_aborted(result_data["time"], output_path, log)
            return

        print_generation_end(result_data["time"], output_path, log)
    finally:
        close_log()


if __name__ == "__main__":
    generate_n1()
