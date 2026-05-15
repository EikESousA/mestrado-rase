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

from config.models import MODEL_NAMES
from utils.generates.generate_config import generate_config
from utils.generates.invoke_with_timeout import invoke_with_timeout
from utils.generates.meta import build_meta, env_seed
from utils.generates.reset_model import reset_model
from utils.generates.resume import (
    append_checkpoint,
    clear_checkpoint,
    load_existing_output,
)
from utils.logs.init_log import init_log
from utils.n1.empty_operators import empty_operators
from utils.n1.process_text import process_text


PROMPT_PATH: Path = Path("prompts") / "n1.txt"


def generate_n1(
    input_path: str | None = None,
    output_path: str | None = None,
    model_id: str | None = None,
    log_path: str | None = None,
) -> None:
    if input_path is None or output_path is None or model_id is None:
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
        args: argparse.Namespace = parser.parse_args()

        input_path, output_path, model_id = generate_config("n1", args.model)
        input_path = str(input_path)
        output_path = str(output_path)
        model_id = str(model_id)
        if args.input_path:
            input_path = args.input_path
        if args.output_path:
            output_path = args.output_path
        log_path = log_path or args.log_path

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

    try:
        template: str = PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("Erro: prompt n1 nao encontrado em prompts/n1.txt.")
        return

    seed = env_seed()
    keep_alive = os.environ.get("N1_KEEP_ALIVE", "30s").strip()

    llm_kwargs: Dict[str, Any] = {
        "model": model_id,
        "temperature": 0.1,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "num_predict": 512,
        "stop": ["TEXTO_INICIO", "TEXTO_FIM", "Entrada:", "Saida:"],
        "client_kwargs": {"timeout": 600},
    }
    if seed is not None:
        llm_kwargs["seed"] = seed
    if keep_alive:
        llm_kwargs["keep_alive"] = keep_alive
    llm: OllamaLLM = OllamaLLM(**llm_kwargs)
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
    chain: RunnableSerializable[Dict[str, str], str] = prompt | llm

    existing = load_existing_output(output_path)
    resume_from = len(existing.get("datas", [])) if existing else 0
    result_data: Dict[str, Any] = {
        "meta": build_meta(model_id=model_id, prompt_text=template, seed=seed),
        "counts": resume_from,
        "datas": list(existing.get("datas", [])) if existing else [],
        "time": float(existing.get("time", 0.0)) if existing else 0.0,
    }
    total_start_time: float = time.time() - result_data["time"]

    if resume_from == 0:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, ensure_ascii=False, indent=2)
        clear_checkpoint(output_path)
    else:
        log(f"Retomando execucao a partir do item {resume_from + 1}.")

    log(
        f"Inicio geracao N1. Modelo={model_id} Entrada={input_path} Saida={output_path}"
    )
    log(f"Total de textos: {len(data.get('datas', []))} (ja processados: {resume_from})")

    try:
        for count, item in enumerate(data["datas"], start=1):
            if count <= resume_from:
                continue
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
                env_debug = os.getenv("GENERATE_DEBUG", "1").strip().lower()
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

            append_checkpoint(output_path, result_entry)
            tmp_path = output_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp_path, output_path)

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
