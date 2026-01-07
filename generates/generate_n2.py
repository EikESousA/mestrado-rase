import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

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
from utils.n2.build_operators import build_operators
from utils.n2.process_text import process_text


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
        log_path = args.log_path

    if input_path is None or output_path is None or model_id is None:
        print("Erro: parametros obrigatorios nao encontrados.")
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
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
        "Inicio geracao N2. "
        f"Modelo={model_id} Entrada={input_path} Saida={output_path}"
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

                for attempt in range(1, 4):
                    log(
                        "Chamando modelo "
                        f"(texto {count}, sentenca {n1_index}, tentativa {attempt})"
                    )
                    try:
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
    generate_n2()
