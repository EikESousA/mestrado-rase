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
from utils.generates.meta import build_meta, env_seed
from utils.generates.resume import (
    append_checkpoint,
    clear_checkpoint,
    load_existing_output,
)
from utils.generates.invoke_with_timeout import invoke_with_timeout
from utils.generates.reset_model import reset_model
from utils.logs.init_log import init_log
from utils.n2.build_operators import build_operators
from utils.n2.process_text import process_text


PROMPT_PATH: Path = Path("prompts") / "n2.txt"


def generate_n2(
    input_path: str | None = None,
    output_path: str | None = None,
    model_id: str | None = None,
    log_path: str | None = None,
) -> None:
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
        args: argparse.Namespace = parser.parse_args()

        input_path, output_path, model_id = generate_config("n2", args.model)
        input_path = str(input_path)
        output_path = str(output_path)
        model_id = str(model_id)
        if args.input_path:
            input_path = args.input_path
        if args.output_path:
            output_path = args.output_path
        log_path = args.log_path

    if input_path is None or output_path is None or model_id is None:
        print("Erro: parametros obrigatorios nao encontrados.")
        return

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

    seed = env_seed()

    def _env_int(name: str, default: int) -> int:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    def _env_float(name: str, default: float) -> float:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return default
        try:
            return float(raw)
        except ValueError:
            return default

    num_predict = _env_int("N2_NUM_PREDICT", 512)
    keep_alive = os.environ.get("N2_KEEP_ALIVE", "30s").strip()
    pause_between_texts = _env_float("N2_TEMP_PAUSE", 2.0)

    llm_kwargs: Dict[str, Any] = {
        "model": model_id,
        "temperature": 0.1,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "num_predict": num_predict,
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
        log(f"Retomando execucao N2 a partir do item {resume_from + 1}.")

    log(
        "Inicio geracao N2. "
        f"Modelo={model_id} Entrada={input_path} Saida={output_path}"
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

            log(f"Iniciando Texto {count}: {preview}{suffix}")
            texts_n1: List[Dict[str, Any]] = []
            for n1_index, n1_item in enumerate(item.get("texts_n1", []), start=1):
                text_n1 = n1_item.get("text_n1", "")
                processed_result: Dict[str, str] = {}

                for attempt in range(1, 4):
                    log(
                        "Chamando modelo "
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
                            log(msg)
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
                            "Erro na chamada do modelo "
                            f"(texto {count}, sentenca {n1_index}, "
                            f"tentativa {attempt}): {exc}"
                        )
                        if attempt < 3:
                            time.sleep(1)
                        continue

                    log(f"Saida do modelo:\n{result}")
                    env_debug = os.getenv("GENERATE_DEBUG", "1").strip().lower()
                    if env_debug in {"1", "true", "yes", "on"}:
                        print("Saida do modelo:")
                        print(result)
                    processed_result = process_text(result)
                    break

                if not processed_result:
                    msg = (
                        "Falha ao processar texto "
                        f"(texto {count}, sentenca {n1_index})."
                    )
                    print(msg)
                    log(msg)
                operators_n2 = build_operators(processed_result)
                texts_n1.append(
                    {
                        "text_n1": text_n1,
                        "operators_n2": operators_n2,
                    }
                )

            end_time: float = time.time()
            elapsed_time: float = end_time - start_time

            result_entry: Dict[str, Any] = {
                "text": item["text"],
                "texts_n1": texts_n1,
            }

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

            if pause_between_texts > 0:
                log(f"Pausa termica de {pause_between_texts:.1f}s.")
                time.sleep(pause_between_texts)
    finally:
        close_log()

    print(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")
    log(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    log(f"Resultado salvo em {output_path}")


if __name__ == "__main__":
    generate_n2()
