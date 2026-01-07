import argparse
import json
import os
import re
import subprocess
import threading
import time
import unicodedata
from pathlib import Path
import sys
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain_ollama import OllamaLLM

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.generate_utils import generate_config


def empty_properties_n3() -> Dict[str, str]:
    return {
        "type": "",
        "object": "",
        "property": "",
        "comparation": "",
        "target": "",
        "unit": "",
    }


def normalize_field_name(field: str) -> str:
    field = unicodedata.normalize("NFKD", field).encode("ASCII", "ignore").decode("ASCII")
    field = field.lower()

    if field == "selecao":
        return "selecao"
    if field in {"execao", "excecao", "execcao"}:
        return "execao"
    if field == "aplicabilidade":
        return "aplicabilidade"
    if field == "requisito":
        return "requisito"
    return field


def clean_output(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"(?i)^(resposta|saida)\s*:\s*", "", cleaned)
    return cleaned.strip()


def process_text(text: str) -> Dict[str, str]:
    campos = ["aplicabilidade", "selecao", "execao", "requisito"]
    resultado = {campo: "" for campo in campos}

    cleaned = clean_output(text)
    padrao_campo = re.compile(r"^(.+?):\s*(.*)$", re.IGNORECASE)
    padrao_checagem = re.compile(rf"^({'|'.join(campos)}):$", re.IGNORECASE)

    campo_atual = None
    for linha in cleaned.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        match = padrao_campo.match(linha)
        if match:
            raw_field = match.group(1).strip()
            campo = normalize_field_name(raw_field)
            valor = match.group(2).strip()

            if campo not in resultado:
                continue

            if padrao_checagem.match(valor.lower()):
                valor = ""

            resultado[campo] = valor
            campo_atual = campo if valor == "" else None
        elif campo_atual:
            if not padrao_campo.match(linha):
                resultado[campo_atual] += " " + linha.strip()

    return {k: v.strip() for k, v in resultado.items()}


def build_operators_n2(result: Dict[str, str]) -> Dict[str, Any]:
    return {
        "requeriments": {
            "text_n2": result.get("requisito", ""),
            "properties_n3": empty_properties_n3(),
        },
        "aplicability": {
            "text_n2": result.get("aplicabilidade", ""),
            "properties_n3": empty_properties_n3(),
        },
        "selection": {
            "text_n2": result.get("selecao", ""),
            "properties_n3": empty_properties_n3(),
        },
        "exception": {
            "text_n2": result.get("execao", ""),
            "properties_n3": empty_properties_n3(),
        },
    }


def generate_n2(
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

    if log_enabled and log_path is not None:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        log_file = open(log_path, "a", encoding="utf-8")
        log(
            "Inicio geracao N2. "
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
                    processed_result = process_text(result)
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
        if log_file is not None:
            log_file.close()
            log_file = None

    print(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")
    log(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    log(f"Resultado salvo em {output_path}")


template = """
Extrator RASE N2.
Use APENAS o Texto N1 para extrair os elementos. O Texto completo e apenas referencia.

Regras (ordem fixa):
1) aplicabilidade (opcional): onde/quando se aplica, sem verbos.
2) selecao (opcional): subconjunto da aplicabilidade, sem verbos.
3) execao (opcional): casos que NAO seguem a regra.
4) requisito (obrigatorio): acao/condicao principal, comeca com verbo.

Regras de saida:
- Retorne exatamente 4 linhas no formato abaixo.
- Cada campo deve aparecer no maximo uma vez.
- Se nao existir, use "" (string vazia).
- Nao adicione explicacoes, listas ou texto extra.

Exemplo (formato):
Texto completo:
"As areas ... Norma."
Texto N1:
"As areas de qualquer espaco ou edificacao de uso publico ou coletivo devem ser servidas de uma ou mais rotas acessiveis."
Resposta (4 linhas):
aplicabilidade: As areas de qualquer espaco ou edificacao
selecao: uso publico ou coletivo
execao: ""
requisito: devem ser servidas de uma ou mais rotas acessiveis

Agora processe:
Texto completo:
"{text}"
Texto N1:
"{text_n1}"

Resposta (4 linhas):
aplicabilidade:
selecao:
execao:
requisito:
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerar operadores RASE N2.")
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

    input_path, output_path, model_id = generate_config("n2", args.model)
    if args.input_path:
        input_path = args.input_path
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_n2(
        input_path=input_path,
        output_path=output_path,
        template=template,
        model=model_id,
        log_path=args.log_path,
    )


if __name__ == "__main__":
    main()
