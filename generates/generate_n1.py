import argparse
import json
import os
import threading
import time
from pathlib import Path
import sys
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import OllamaLLM

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.generate_n1_utils import empty_operators, process_text
from utils.generate_utils import generate_config


def generate_n1(
    input_path: str,
    output_path: str,
    template: str,
    model: str,
    max_retries: int = 2,
    log_path: str | None = None,
    call_timeout: float = 180.0,
    heartbeat_interval: float = 30.0,
) -> None:
    data: Dict[str, Any] = {}
    log_file = None
    log_enabled = False
    if log_path is None:
        env_debug = os.getenv("GENERATE_DEBUG", "").strip().lower()
        if env_debug in {"1", "true", "yes", "on"}:
            output_name = Path(output_path).name
            log_path = str(Path("logs") / f"{output_name}.log")
    if log_path is not None:
        log_enabled = True

    def log(message: str) -> None:
        if not log_enabled or log_file is None:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        log_file.write(line + "\n")
        log_file.flush()

    def invoke_with_timeout(text: str) -> tuple[str | None, bool]:
        result_holder: Dict[str, str] = {}
        error_holder: Dict[str, Exception] = {}

        def _run() -> None:
            try:
                result_holder["result"] = chain.invoke({"text": text})
            except Exception as exc:
                error_holder["error"] = exc

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        start = time.time()
        next_heartbeat = start + heartbeat_interval
        while thread.is_alive():
            now = time.time()
            if now >= start + call_timeout:
                return None, True
            if heartbeat_interval > 0 and now >= next_heartbeat:
                log(
                    "Ainda aguardando resposta do modelo "
                    f"({int(now - start)}s)..."
                )
                next_heartbeat = now + heartbeat_interval
            time.sleep(0.2)

        if "error" in error_holder:
            raise error_holder["error"]
        return result_holder.get("result"), False

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Erro: Arquivo de entrada nao encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro: Falha ao decodificar JSON de entrada.")
        return

    llm: OllamaLLM = OllamaLLM(
        model=model,
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

    if log_enabled and log_path is not None:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")
        log(
            f"Inicio geracao N1. Modelo={model} Entrada={input_path} Saida={output_path}"
        )
        log(f"Total de textos: {len(data.get('datas', []))}")

    try:
        for count, item in enumerate(data["datas"], start=1):
            raw_text = item["text"].replace("\n", " ").strip()
            preview = raw_text[:40].rstrip()
            suffix = "..." if len(raw_text) > 40 else ""
            start_time: float = time.time()
            result = ""
            processed_result: List[str] = []

            log(f"Iniciando Texto {count}: {preview}{suffix}")
            for attempt in range(1, max_retries + 1):
                log(f"Chamando modelo (tentativa {attempt})")
                try:
                    result, timed_out = invoke_with_timeout(item["text"])
                    if timed_out:
                        msg = (
                            "Timeout na chamada do modelo "
                            f"apos {int(call_timeout)}s."
                        )
                        print(msg)
                        log(msg)
                        continue
                    if result is None:
                        raise RuntimeError("Resposta vazia do modelo.")
                except Exception as exc:
                    print(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    log(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    if attempt < max_retries:
                        time.sleep(1)
                    continue
                processed_result = process_text(result)
                if processed_result:
                    break
                print(f"Tentativa {attempt} retornou vazio. Repetindo.")
                log(f"Tentativa {attempt} retornou vazio. Repetindo.")
            end_time: float = time.time()

            elapsed_time: float = end_time - start_time
            texts_n1 = [
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
        if log_file is not None:
            log_file.close()
            log_file = None

    print(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")
    log(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    log(f"Resultado salvo em {output_path}")


template = """
Voce e um reescritor. Transforme o texto em sentencas RASE N1.

Regras:
1) Quebre em sentencas curtas e diretas.
2) Cada sentenca deve ter uma unica regra computavel.
3) Nao invente elementos (aplicabilidade, selecao, requisito, excecao). Preserve apenas o que existir.
4) Nao adicione explicacoes, titulos, bullets, numeracao ou o texto original.
5) Saida: apenas as sentencas, uma por linha, terminadas com ponto final.

Exemplo:
Entrada:
A inclinacao transversal da superficie deve ser de ate 2 % para pisos internos e de ate 3 % para pisos externos.
Saida:
Pisos internos devem ter inclinacao transversal de no maximo 2%.
Pisos externos devem ter inclinacao transversal de no maximo 3%.

TEXTO_INICIO
{text}
TEXTO_FIM
"""


def main() -> None:
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
    args = parser.parse_args()

    input_path, output_path, model_id = generate_config("n1", args.model)
    if args.input_path:
        input_path = args.input_path
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_n1(
        input_path=input_path,
        output_path=output_path,
        template=template,
        model=model_id,
        log_path=args.log_path,
    )


if __name__ == "__main__":
    main()
