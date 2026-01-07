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

from utils.generates.generate_config import generate_config
from utils.generates.invoke_with_timeout import invoke_with_timeout
from utils.generates.reset_model import reset_model
from utils.logs.init_log import init_log
from utils.n1.empty_operators import empty_operators
from utils.n1.process_text import process_text


PROMPT_PATH: Path = Path("prompts") / "n1.txt"


def generate_n1() -> None:
    parser = argparse.ArgumentParser(description="Gerar sentencas RASE N1.")
    parser.add_argument(
        "--model",
        choices=["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"],
        default="mistral",
        help="Modelo base para geracao.",
    )
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)
    parser.add_argument("--log", dest="log_path", default=None)
    args: argparse.Namespace = parser.parse_args()

    input_path, output_path, model_id = generate_config("n1", args.model)
    input_path: str = str(input_path)
    output_path: str = str(output_path)
    model_id: str = str(model_id)
    if args.input_path:
        input_path = args.input_path
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

    llm: OllamaLLM = OllamaLLM(
        model=model_id,
        temperature=0.1,
        top_p=0.9,
        repeat_penalty=1.1,
        client_kwargs={"timeout": 600},
    )
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
    chain: RunnableSerializable[Dict[str, str], str] = prompt | llm

    result_data: Dict[str, Any] = {"counts": 0, "datas": [], "time": 0.0}
    total_start_time: float = time.time()

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, ensure_ascii=False, indent=2)

    log(
        f"Inicio geracao N1. Modelo={model_id} Entrada={input_path} Saida={output_path}"
    )
    log(f"Total de textos: {len(data.get('datas', []))}")

    try:
        for count, item in enumerate(data["datas"], start=1):
            raw_text = item["text"].replace("\n", " ").strip()
            preview = raw_text[:40].rstrip()
            suffix = "..." if len(raw_text) > 40 else ""
            start_time: float = time.time()
            processed_result: List[str] = []

            log(f"Iniciando Texto {count}: {preview}{suffix}")
            for attempt in range(1, 4):
                log(f"Chamando modelo (tentativa {attempt})")
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
                        log(msg)
                        reset_model(model_id, log)
                        continue
                    if result is None:
                        raise RuntimeError("Resposta vazia do modelo.")
                except Exception as exc:
                    print(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    log(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    if attempt < 3:
                        time.sleep(1)
                    continue
                log(f"Saida do modelo:\n{result}")
                env_debug = os.getenv("GENERATE_DEBUG", "").strip().lower()
                if env_debug in {"1", "true", "yes", "on"}:
                    print("Saida do modelo:")
                    print(result)
                processed_result = process_text(result)
                if processed_result:
                    break
                print(f"Tentativa {attempt} retornou vazio. Repetindo.")
                log(f"Tentativa {attempt} retornou vazio. Repetindo.")
            end_time: float = time.time()

            elapsed_time: float = end_time - start_time
            if not processed_result:
                msg = (
                    "Falha ao processar texto "
                    "apos 3 tentativas. Seguindo."
                )
                print(msg)
                log(msg)
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

            print(f"Texto {count} ({elapsed_time:.2f}s): {preview}{suffix}")
            log(f"Texto {count} concluido ({elapsed_time:.2f}s)")
    finally:
        close_log()

    print(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")
    log(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    log(f"Resultado salvo em {output_path}")


if __name__ == "__main__":
    generate_n1()
