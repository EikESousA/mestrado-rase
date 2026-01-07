import json
import re
import time
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import OllamaLLM

from utils.generate_utils import invoke_with_timeout, reset_model
from utils.log_utils import init_log

def empty_operators() -> Dict[str, str]:
    return {
        "requeriments": "",
        "aplicability": "",
        "selection": "",
        "exception": "",
    }


def clean_output(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"(?i)^(resposta|saida)\s*:\s*", "", cleaned)
    cleaned = cleaned.strip().strip('"').strip("'").strip()
    return cleaned


def split_sentences(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [text.strip()]

    sentences: List[str] = []
    for line in lines:
        line = re.sub(r"^\s*[-*]\s+", "", line)
        line = re.sub(r"^\s*\d+[\).\s-]+\s*", "", line)
        if not line:
            continue
        parts = re.split(r"(?<!\b[A-Z])\.\s+(?![a-z])", line)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if not part.endswith("."):
                part += "."
            sentences.append(part)

    deduped: List[str] = []
    seen = set()
    for sentence in sentences:
        if sentence not in seen:
            deduped.append(sentence)
            seen.add(sentence)

    return deduped


def process_text(text: str) -> List[str]:
    cleaned = clean_output(text)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return split_sentences(cleaned)


def generate_n1(
    input_path: str,
    output_path: str,
    template: str,
    model: str,
    max_retries: int = 3,
    log_path: str | None = None,
    call_timeout: float = 600.0,
    heartbeat_interval: float = 60.0,
) -> None:
    data: Dict[str, Any] = {}
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
                    result, timed_out = invoke_with_timeout(
                        chain,
                        {"text": item["text"]},
                        call_timeout,
                        heartbeat_interval,
                        log,
                    )
                    if timed_out:
                        msg = (
                            "Timeout na chamada do modelo "
                            f"apos {int(call_timeout)}s."
                        )
                        print(msg)
                        log(msg)
                        reset_model(model, log)
                        continue
                    if result is None:
                        raise RuntimeError("Resposta vazia do modelo.")
                except Exception as exc:
                    print(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    log(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                    if attempt < max_retries:
                        time.sleep(1)
                    continue
                log(f"Saida do modelo:\n{result}")
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
                    f"apos {max_retries} tentativas. Seguindo."
                )
                print(msg)
                log(msg)
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
        close_log()

    print(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")
    log(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    log(f"Resultado salvo em {output_path}")
