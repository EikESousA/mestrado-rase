import json
import re
import time
from typing import Dict, Any, Literal, Tuple
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
import unicodedata

Tipo = Literal["n1", "n2", "n3"]
Modelo = Literal["llama", "alpaca", "mistral", "dolphin"]

def generate_config(tipo: Tipo, modelo: Modelo) -> Tuple[str, str, str]:
    input_file = f"../databases/data_{tipo}.json"

    modelos = {
        "llama": {
            "output_file": f"../databases/generate_{tipo}_llama.json",
            "model": "llama3.3:latest"
        },
        "alpaca": {
            "output_file": f"../databases/generate_{tipo}_alpaca.json",
            "model": "splitpierre/bode-alpaca-pt-br:latest"
        },
        "mistral": {
            "output_file": f"../databases/generate_{tipo}_mistral.json",
            "model": "cnmoro/mistral_7b_portuguese:q2_K"
        },
        "dolphin": {
            "output_file": f"../databases/generate_{tipo}_dolphin.json",
            "model": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m"
        }
    }

    output_file = modelos[modelo]["output_file"]
    model = modelos[modelo]["model"]

    return input_file, output_file, model

def normalize_field_name(field: str) -> str:
    # Remove acentos
    field = unicodedata.normalize("NFKD", field).encode("ASCII", "ignore").decode("ASCII")
    field = field.lower()

    # Mapeia variações para os nomes esperados
    if field in ["selecao", "selecao", "seleçao", "seleção"]:
        return "selecao"
    elif field in ["execao", "excecao", "exceção", "execcao", "exeçao", "exeção"]:
        return "execao"
    elif field == "aplicabilidade":
        return "aplicabilidade"
    elif field == "requisito":
        return "requisito"
    return field 

def process_text(texto: str) -> Dict[str, str]:
    campos = ["aplicabilidade", "selecao", "execao", "requisito"]
    resultado = {campo: "" for campo in campos}

    padrao_campo = re.compile(rf"^(.+?):\s*(.*)$", re.IGNORECASE)
    padrao_checagem = re.compile(rf"^({'|'.join(campos)}):$", re.IGNORECASE)

    campo_atual = None
    linhas = texto.splitlines()

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue

        match = padrao_campo.match(linha)
        if match:
            raw_field = match.group(1).strip()
            campo = normalize_field_name(raw_field)
            valor = match.group(2).strip()

            if campo not in resultado:
                continue  # ignora campos inesperados

            if padrao_checagem.match(valor.lower()):
                valor = ""

            resultado[campo] = valor
            campo_atual = campo if valor == "" else None
        elif campo_atual:
            if not padrao_campo.match(linha):
                resultado[campo_atual] += " " + linha.strip()

    resultado = {k: v.strip() for k, v in resultado.items()}
    return resultado

def generate_n2(input_path: str, output_path: str, template: str, model: str) -> None:
    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Erro: Arquivo de entrada não encontrado.")
        return
    except json.JSONDecodeError:
        print("Erro: Falha ao decodificar JSON de entrada.")
        return

    llm: OllamaLLM = OllamaLLM(model=model)
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(template)
    chain: RunnableSerializable[Dict[str, str], str] = prompt | llm

    result_data: Dict[str, Any] = {"count": 0, "datas": [], "time": 0.0}
    total_start_time: float = time.time()

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result_data, file, ensure_ascii=False, indent=4)

    for count, item in enumerate(data["datas"], start=1):
        start_time: float = time.time()
        full_response: str = chain.invoke({"transform": item["transform"]})
        processed_result: Dict[str, str] = process_text(full_response)
        end_time: float = time.time()

        elapsed_time: float = end_time - start_time
        result_entry: Dict[str, Any] = {
            "transform": item["transform"],
            "text": item["text"],
            "result": processed_result,
            "full": full_response,
            "time": elapsed_time,
        }

        result_data["datas"].append(result_entry)
        result_data["count"] = count
        result_data["time"] = time.time() - total_start_time

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, ensure_ascii=False, indent=4)

        print(f"Processando {count}: {item['transform']}")
        print(f"Retorno do modelo:\n{processed_result}")
        print(f"Tempo gasto: {elapsed_time:.2f} segundos\n")

    print(f"Processamento concluído. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")

template = """
A metodologia **RASE N2** transforma textos normativos em uma estrutura organizada, garantindo que cada parte do texto apareça apenas uma vez, respeitando a seguinte ordem:

---

### **1. Aplicabilidade (Opcional)**
- **Onde ou quando a regra se aplica.**
- **Deve ser extraída primeiro, antes de outros elementos.**
- **Extraído SOMENTE do TEXTO N1.**
- **NÃO pode conter verbos, ações ou condições.**
- **Se não houver aplicabilidade, retornar `""` (string vazia).**

### **2. Seleção (Opcional)**
- **Parte mais específica da aplicabilidade.**
- **Extraído SOMENTE do TEXTO N1, após a remoção de aplicabilidade.**
- **Deve ser um subconjunto da aplicabilidade, sem repetir o requisito.**
- **NÃO pode conter verbos, ações ou condições.**
- **Se não houver seleção, retornar `""` (string vazia).**

### **3. Exceção (Opcional)**
- **Casos que NÃO precisam seguir a regra.**
- **Extraído SOMENTE do TEXTO N1, após a remoção de aplicabilidade e seleção.**
- **Se um elemento for uma exceção, ele não pode estar em outro campo.**
- **Se não houver, retornar `""` (string vazia).**

### **4. Requisito (Obrigatório)**
- **O que deve ser feito (ação ou condição).**
- **Extraído SOMENTE do TEXTO N1, após a remoção de aplicabilidade, seleção e exceção.**
- **NÃO pode conter informações da aplicabilidade, seleção ou exceção.**
- **O requisito deve começar com um verbo e expressar uma ação ou condição clara.**

---

## **Regras obrigatórias**
**Os elementos devem ser extraídos APENAS do Texto N1.**
**Cada parte do texto deve aparecer apenas uma vez, na ordem Aplicabilidade > Seleção > Exceção > Requisito.**
**Se um elemento não existir, retornar `""` (string vazia).**
**O requisito deve ser a ação ou condição principal e nunca pode ser colocado na seleção.**
**A seleção deve ser um subconjunto da aplicabilidade e não pode conter ações.**
**O requisito deve começar com um verbo e expressar uma ação clara.**
**Retorne somente as resposta.**

---

### **Agora, processe o seguinte texto:**

**Texto N1:**
"{transform}"

#### **Resposta:**
aplicabilidade:
selecao:
execao:
requisito:
"""

input_file, output_file, model = generate_config("n2", "llama")

generate_n2(input_file, output_file, template, model)