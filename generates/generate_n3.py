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
from utils.n2.empty_properties import empty_properties
from utils.n3.parse_properties import parse_properties


PROMPT_PATHS: Dict[str, Path] = {
    "aplicability": Path("prompts") / "n3_aplicabilidade.txt",
    "selection": Path("prompts") / "n3_selecao.txt",
    "exception": Path("prompts") / "n3_execao.txt",
    "requeriments": Path("prompts") / "n3_requisito.txt",
}


def _escape_braces(template: str, variables: List[str]) -> str:
    escaped = template.replace("{", "{{").replace("}", "}}")
    for var in variables:
        escaped = escaped.replace("{{" + var + "}}", "{" + var + "}")
    return escaped


_LEGACY_VARS_BY_KEY: Dict[str, List[str]] = {
    "aplicability": ["text", "text_n1", "aplicabilidade"],
    "selection": ["text", "text_n1", "selecao"],
    "exception": ["text", "text_n1", "execao"],
    "requeriments": ["text", "text_n1", "requisito"],
}

INPUT_KEYS: Dict[str, str] = {
    "aplicability": "aplicabilidade",
    "selection": "selecao",
    "exception": "execao",
    "requeriments": "requisito",
}

TYPE_BY_OPERATOR: Dict[str, str] = {
    "aplicability": "aplicabilidade",
    "selection": "selecao",
    "exception": "excecao",
    "requeriments": "requisito",
}


def _process_per_operator(
    chains: Dict[str, RunnableSerializable[Dict[str, str], str]],
    item: Dict[str, Any],
    text_n1: str,
    operators_n2: Dict[str, Any],
    model_id: str,
    count: int,
    n1_index: int,
    log: Callable[[str], None],
) -> None:
    for op_key, input_key in INPUT_KEYS.items():
        operator = operators_n2.get(op_key, {})
        text_n2 = operator.get("text_n2", "").strip()
        if not text_n2:
            operator["properties_n3"] = empty_properties()
            continue

        processed: Dict[str, str] = {}
        for attempt in range(1, 4):
            log(
                "Chamando modelo "
                f"(texto {count}, sentenca {n1_index}, "
                f"operador {op_key}, tentativa {attempt})"
            )
            try:
                result, timed_out = invoke_with_timeout(
                    chains[op_key],
                    {
                        input_key: text_n2,
                        "text": item.get("text", ""),
                        "text_n1": text_n1,
                    },
                    600.0,
                    60.0,
                    log,
                )
                if timed_out:
                    msg = f"Timeout na chamada do modelo apos {int(600.0)}s."
                    print(msg)
                    log(msg)
                    reset_model(model_id, log)
                    continue
                if result is None:
                    raise RuntimeError("Resposta vazia do modelo.")
            except Exception as exc:
                log(f"Erro op={op_key} tentativa={attempt}: {exc}")
                if attempt < 3:
                    time.sleep(1)
                continue

            log(f"Saida do modelo ({op_key}):\n{result}")
            processed = parse_properties(result)
            if processed != empty_properties():
                break

        if not processed:
            processed = empty_properties()
        if not processed.get("type"):
            processed["type"] = TYPE_BY_OPERATOR[op_key]
        operator["properties_n3"] = processed
        operators_n2[op_key] = operator


def generate_n3(
    input_path: str | None = None,
    output_path: str | None = None,
    model_id: str | None = None,
    log_path: str | None = None,
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
        args: argparse.Namespace = parser.parse_args()

        input_path, output_path, model_id = generate_config("n3", args.model)
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

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    log, close_log = init_log(output_path, log_path)

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data: Dict[str, Any] = json.load(file)
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

    num_predict = _env_int("N3_NUM_PREDICT", 1024)
    keep_alive = os.environ.get("N3_KEEP_ALIVE", "30s").strip()
    pause_between_texts = _env_float("N3_TEMP_PAUSE", 4.0)

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

    chains: Dict[str, RunnableSerializable[Dict[str, str], str]] = {}

    try:
        templates = {
            key: path.read_text(encoding="utf-8")
            for key, path in PROMPT_PATHS.items()
        }
    except FileNotFoundError as exc:
        print(f"Erro: prompt N3 nao encontrado ({exc}).")
        return
    for key, template in templates.items():
        safe_template = _escape_braces(template, _LEGACY_VARS_BY_KEY[key])
        prompt = ChatPromptTemplate.from_template(safe_template)
        chains[key] = prompt | llm
    prompt_for_meta = "\n---\n".join(templates.values())

    existing = load_existing_output(output_path)
    resume_from = len(existing.get("datas", [])) if existing else 0
    result_data: Dict[str, Any] = {
        "meta": build_meta(
            model_id=model_id,
            prompt_text=prompt_for_meta,
            seed=seed,
            extra={"mode": "legacy"},
        ),
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
        log(f"Retomando execucao N3 a partir do item {resume_from + 1}.")

    log(
        f"Inicio geracao N3 [legacy (4 calls/sentenca)]. Modelo={model_id} "
        f"Entrada={input_path} Saida={output_path}"
    )
    log(f"Total de textos: {len(data.get('datas', []))} (ja processados: {resume_from})")

    try:
        for count, item in enumerate(data.get("datas", []), start=1):
            if count <= resume_from:
                continue
            raw_text = item.get("text", "").replace("\n", " ").strip()
            preview = raw_text[:40].rstrip()
            suffix = "..." if len(raw_text) > 40 else ""
            start_time: float = time.time()

            log(f"Iniciando Texto {count}: {preview}{suffix}")
            texts_n1 = []

            for n1_index, n1_item in enumerate(item.get("texts_n1", []), start=1):
                text_n1 = n1_item.get("text_n1", "")
                operators_n2 = n1_item.get("operators_n2", {})

                _process_per_operator(
                    chains, item, text_n1, operators_n2,
                    model_id, count, n1_index, log,
                )

                texts_n1.append(
                    {"text_n1": text_n1, "operators_n2": operators_n2}
                )

            elapsed_time = time.time() - start_time
            result_entry: Dict[str, Any] = {
                "text": item.get("text", ""),
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
    generate_n3()
