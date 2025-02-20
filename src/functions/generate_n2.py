from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Template atualizado para seguir rigorosamente a metodologia RASE N2
template = """
A metodologia **RASE N2** transforma textos normativos em uma estrutura organizada com os seguintes elementos:

### **1. Requisito (Obrigatório)**  
- **O que deve ser feito** (ação ou condição).  
- **Deve ser extraído SOMENTE do TEXTO N1.**  
- **NÃO pode conter o objeto da regra (aplicabilidade).**  

### **2. Aplicabilidade (Opcional)**  
- **Onde ou quando a regra se aplica** (exemplo: "Os acessos", "As escadas").  
- **NÃO pode conter verbos ou ações.**  
- **Deve ser removida do requisito se estiver presente lá.**  
- **Se não houver aplicabilidade, retornar `""` (string vazia).**  

### **3. Seleção (Opcional)**  
- **Subconjunto da aplicabilidade.**  
- **Só pode existir se houver aplicabilidade.**  
- **Se não houver, retornar `""`.**  

### **4. Exceção (Opcional)**  
- **Casos que NÃO precisam seguir a regra.**  
- **Se não houver, retornar `""`.**  

---

## **Regras obrigatórias**  
✅ **O requisito deve vir SOMENTE do TEXTO N1.**  
✅ **A aplicabilidade deve ser um objeto/área e não pode conter verbos.**  
✅ **Se um elemento não existir, retornar `""` (string vazia), nunca "Nenhum selecionável" ou "None".**  
✅ **Se um elemento estiver dentro do requisito, ele deve ser removido do requisito.**  

---

### **Exemplo 1**  

#### **Entrada:**  
**Texto Completo:**  
"As áreas de qualquer espaço ou edificação de uso público ou coletivo devem ser servidas de uma ou mais rotas acessíveis."  

**Texto N1:**  
"As áreas de qualquer espaço ou edificação de uso público ou coletivo devem ser servidas de uma ou mais rotas acessíveis."  

#### **Saída Correta:**  
requisito: "devem ser servidas de uma ou mais rotas acessíveis"  
aplicabilidade: "As áreas de qualquer espaço ou edificação"  
selecao: "uso público ou coletivo"  
execcao: ""  

---

### **Exemplo 2**  

#### **Entrada:**  
**Texto Completo:**  
"As áreas de qualquer espaço ou edificação de uso público ou coletivo devem ser servidas de uma ou mais rotas acessíveis. Áreas de uso restrito, conforme definido em 3.1.38, como casas de máquinas, barriletes, passagem de uso técnico e outros com funções similares, não necessitam atender às condições de acessibilidade desta Norma."  

**Texto N1:**  
"Áreas de uso restrito, conforme definido em 3.1.38, como casas de máquinas, barriletes, passagem de uso técnico e outros com funções similares, não necessitam atender às condições de acessibilidade desta Norma."  

#### **Saída Correta:**  
requisito: "não necessitam atender às condições de acessibilidade desta Norma"  
aplicabilidade: ""  
selecao: ""  
execcao: "Áreas de uso restrito, conforme definido em 3.1.38, como casas de máquinas, barriletes, passagem de uso técnico e outros com funções similares"  

---

### **Agora, processe o seguinte texto:**  

**Texto Completo:**  
"{text}"  

**Texto N1:**  
"{transform}"  

#### **Resposta:**  
requisito:  
aplicabilidade:  
selecao:  
execcao:  
"""

model = OllamaLLM(model="splitpierre/bode-alpaca-pt-br")

prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model
result = chain.invoke({
    "text": "Os acessos devem ser vinculados através de rota acessível à circulação principal e às circulações de emergência. Os acessos devem permanecer livres de quaisquer obstáculos de forma permanente.",
    "transform": "Os acessos devem permanecer livres de quaisquer obstáculos de forma permanente."
})

print(result)
