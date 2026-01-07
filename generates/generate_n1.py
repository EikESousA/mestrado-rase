import argparse
import json
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
) -> None:
    data: Dict[str, Any] = {}

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

    for count, item in enumerate(data["datas"], start=1):
        raw_text = item["text"].replace("\n", " ").strip()
        preview = raw_text[:40].rstrip()
        suffix = "..." if len(raw_text) > 40 else ""
        start_time: float = time.time()
        result = ""
        processed_result: List[str] = []
        for attempt in range(1, max_retries + 1):
            try:
                result = chain.invoke({"text": item["text"]})
            except Exception as exc:
                print(f"Erro na chamada do modelo (tentativa {attempt}): {exc}")
                if attempt < max_retries:
                    time.sleep(1)
                continue
            processed_result = process_text(result)
            if processed_result:
                break
            print(f"Tentativa {attempt} retornou vazio. Repetindo.")
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

		print()
    print(f"Processamento concluido. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")


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
        choices=["llama", "alpaca", "mistral", "dolphin"],
        default="mistral",
        help="Modelo base para geracao.",
    )
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)
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
    )


if __name__ == "__main__":
    main()
