from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import json
import re

def process_text(text: str) -> list:       
    sentences = re.split(r'(?<!\d)(\.)\n|\n|(?<!\d)(\.)(?!\d)', text.strip())
    
    processed_sentences = []
    temp_sentence = ""
    
    for part in sentences:
        if part is None:
            continue
        temp_sentence += part.strip()
        if part.strip() == ".":
            processed_sentences.append(temp_sentence.strip())
            temp_sentence = ""
    
    if temp_sentence:
        processed_sentences.append(temp_sentence.strip())
    
    return processed_sentences
  
def generate_n1(input_path: str, output_path: str, template: str, model: str) -> None:
    """
    Lê um arquivo JSON contendo textos e aplica a metodologia RASE N1, gerando um novo JSON com os textos transformados.

    - Para cada entrada no JSON, o campo "text" é processado e dividido em sentenças menores, mantendo aplicabilidade, 
      seleção, requisito e exceção.
    - O resultado processado é armazenado no campo "texts" da mesma entrada.
    - O novo JSON é salvo no caminho especificado.

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

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
    except FileNotFoundError:
        print("Erro: Arquivo de entrada não encontrado.")
        return
    
    except json.JSONDecodeError:
        print("Erro: Falha ao decodificar JSON de entrada.")
        return

    llm = OllamaLLM(model=model)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    for item in data["datas"]:
        result = chain.invoke({"text": item["text"]})
        item["texts"] = process_text(result)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        
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

input_file: str = "../databases/data_n1.json"
output_file: str = "../databases/generate_n1_llama.json"
model_llama: str = "llama3.3"
model_alpaca: str = "splitpierre/bode-alpaca-pt-br"

generate_n1(input_file, output_file, template, model_llama)
print(f"Processamento concluído. Resultado salvo em {output_file}")