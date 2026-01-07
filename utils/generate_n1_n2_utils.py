import json
import subprocess
import threading
import time
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import OllamaLLM

from utils.generate_utils import build_operators_n2, process_n2_text
from utils.log_utils import init_log


def generate_n1_n2(
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

    def reset_model() -> None:
        try:
            subprocess.run(["ollama", "stop", model], check=False)
        except (subprocess.SubprocessError, FileNotFoundError):
            log("Erro ao descarregar o modelo.")

    def invoke_with_timeout(payload: Dict[str, str], timeout: float) -> tuple[str | None, bool]:
        result_holder: Dict[str, str] = {}
        error_holder: Dict[str, Exception] = {}

        def _run() -> None:
            try:
                result_holder["result"] = chain.invoke(payload)
            except Exception as exc:
                error_holder["error"] = exc

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        start = time.time()
        next_heartbeat = start + heartbeat_interval
        while thread.is_alive():
            now = time.time()
            if now >= start + timeout:
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

    log(
        "Inicio geracao N1->N2. "
        f"Modelo={model} Entrada={input_path} Saida={output_path}"
    )
    log(f"Total de textos: {len(data.get('datas', []))}")

    try:
        for count, item in enumerate(data["datas"], start=1):
            raw_text = item["text"].replace("\n", " ").strip()
            preview = raw_text[:40].rstrip()
            suffix = "..." if len(raw_text) > 40 else ""
            start_time: float = time.time()

            log(f"Iniciando Texto {count}: {preview}{suffix}")
            texts_n1: List[Dict[str, Any]] = []
            for n1_index, n1_item in enumerate(item.get("texts_n1", []), start=1):
                text_n1 = n1_item.get("text_n1", "")
                processed_result: Dict[str, str] = {}

                for attempt in range(1, max_retries + 1):
                    log(
                        "Chamando modelo "
                        f"(texto {count}, sentenca {n1_index}, tentativa {attempt})"
                    )
                    try:
                        result, timed_out = invoke_with_timeout(
                            {"text": item["text"], "text_n1": text_n1},
                            call_timeout,
                        )
                        if timed_out:
                            msg = (
                                "Timeout na chamada do modelo "
                                f"apos {int(call_timeout)}s."
                            )
                            print(msg)
                            log(msg)
                            reset_model()
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
                        if attempt < max_retries:
                            time.sleep(1)
                        continue

                    log(f"Saida do modelo:\n{result}")
                    processed_result = process_n2_text(result)
                    break

                if not processed_result:
                    msg = (
                        "Falha ao processar texto "
                        f"(texto {count}, sentenca {n1_index})."
                    )
                    print(msg)
                    log(msg)
                operators_n2 = build_operators_n2(processed_result)
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
