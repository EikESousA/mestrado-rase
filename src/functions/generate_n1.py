from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json
import re
import time
from typing import Dict, List, Any, Literal, Tuple
from langchain_core.runnables import RunnableSerializable

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

def process_text(text: str) -> List[str]:
    """
    Processa um texto, dividindo-o em sentenças menores.

    - O texto é segmentado com base em pontuação e quebras de linha.
    - Remove espaços extras e mantém a estrutura original das frases.
    - Retorna uma lista de sentenças processadas.

    Parâmetros:
        - text (str): O texto de entrada a ser processado.

    Retorna:
        - list: Lista de sentenças processadas.
    """
    
    text = re.sub(r'\s+', ' ', text.strip())
    
    sentences = re.split(r'(?<!\b[A-Z])\.\s+(?![a-z])', text)

    return [s.strip() + '.' if not s.strip().endswith('.') else s.strip() for s in sentences if s.strip()]

def generate_n1(input_path: str, output_path: str, template: str, model: str) -> None:
    """
    Lê um arquivo JSON contendo textos e aplica a metodologia RASE N1, gerando um novo JSON com os textos transformados.

    - Para cada entrada no JSON, o campo "text" é processado e dividido em sentenças menores, mantendo aplicabilidade, 
      seleção, requisito e exceção.
    - O resultado processado é armazenado no campo "texts" da mesma entrada.
    - O novo JSON é salvo no caminho especificado armazenando a quantidade, os dados e o tempo de processamento.

    Parâmetros:
        - input_path (str): Caminho do arquivo JSON de entrada contendo os textos a serem transformados.
        - output_path (str): Caminho do arquivo JSON de saída onde os textos processados serão armazenados.
        - template (str): Template utilizado para estruturar a solicitação ao modelo de linguagem.
    
    Exceções:
        - FileNotFoundError: Se o arquivo de entrada não for encontrado.
        - JSONDecodeError: Se houver erro ao decodificar o JSON de entrada.

    Retorna:
        - None

    """
    
    data: Dict[str, Any] = {}
    
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
        result: str = chain.invoke({"text": item["text"]})
        processed_result: List[str] = process_text(result)
        end_time: float = time.time()
        
        elapsed_time: float = end_time - start_time
        result_entry: Dict[str, Any] = {"text": item["text"], "texts": processed_result, "time": elapsed_time}
        
        result_data["datas"].append(result_entry)
        result_data["count"] = count
        result_data["time"] = time.time() - total_start_time
        
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, ensure_ascii=False, indent=4)
        
        print(f"Processando {count}: {item['text']}")
        print(f"Retorno do modelo: {processed_result}")
        print(f"Tempo gasto: {elapsed_time:.2f} segundos\n")
    
    print(f"Processamento concluído. Tempo total: {result_data['time']:.2f} segundos.")
    print(f"Resultado salvo em {output_path}")

template = """
A metodologia **RASE N1** transforma textos em unidades menores, onde cada unidade contém **apenas uma única regra computável** com métricas claras.  

### **Instruções:**  
1. **Divida o texto** em sentenças curtas e diretas, respeitando a metodologia **RASE N1**.  
2. **Cada sentença deve conter somente uma única regra computável**.  
3. **Não remova nenhum dos seguintes elementos:**  
   - **Aplicabilidade:** Onde ou quando a regra se aplica.  
   - **Seleção:** Elemento específico dentro da aplicabilidade.  
   - **Requisito:** O que deve ser feito.  
   - **Exceção:** Casos que não precisam seguir a regra.  
4. **A resposta deve conter apenas os textos reformulados, sem explicações ou títulos.**  
5. **Cada frase deve ser separada por `\n`, garantindo uma quebra de linha entre elas.**  
6. **Todas as frases devem ser convertidas em afirmações lógicas.**  

### **Exemplo 1:**  

#### **Entrada:**  
"A inclinação transversal da superfície deve ser de até 2 % para pisos internos e de até 3 % para pisos externos. A inclinação longitudinal da superfície deve ser inferior a 5 %. Inclinações iguais ou superiores a 5 % são consideradas rampas e, portanto, devem atender a 6.6."  

#### **Saída:**  
Pisos internos devem ter inclinação transversal de no máximo 2%.\n  
Pisos externos devem ter inclinação transversal de no máximo 3%.\n  
A inclinação longitudinal da superfície deve ser inferior a 5%.\n  
Inclinações iguais ou superiores a 5% são consideradas rampas e devem atender à norma 6.6.\n  

### **Exemplo 2:**  

#### **Entrada:**  
"Os acessos devem ser vinculados através de rota acessível à circulação principal e às circulações de emergência. Os acessos devem permanecer livres de quaisquer obstáculos de forma permanente."  

#### **Saída:**  
Os acessos devem ser vinculados através de rota acessível à circulação principal e às circulações de emergência.\n  
Os acessos devem permanecer livres de quaisquer obstáculos de forma permanente.\n  

### **Agora, transforme o texto abaixo utilizando a metodologia RASE N1:**  

#### **Texto:**  
{text}  

#### **Resposta:**    
"""

input_file, output_file, model = generate_config("n1", "llama")

generate_n1(input_file, output_file, template, model)