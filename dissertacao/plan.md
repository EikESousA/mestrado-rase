# Plano de Reescrita da Dissertação — `Conteudo/`, `Pre_Textual/` e `mestrado-rase/`

Este documento orienta a reescrita da dissertação para alinhá-la ao que foi efetivamente implementado em `mestrado-rase/`. A pesquisa, originalmente proposta com Fine-Tuning, RAG e integração ao Revit, foi executada de forma diferente: **apenas Engenharia de Prompt**, **6 LLMs *open-source*** comparados, **3 níveis de normalização (N1/N2/N3)**, **3 experimentos (EN1, EN2, EN1N2)** e **avaliação por métricas de similaridade textual + métricas de classificação a adicionar**.

| Arquivo | Capítulo / Função | Status atual | Ação |
|---|---|---|---|
| `Modelo-Mestrado-PROCC.tex` | Raiz LaTeX | Não inclui Conclusão nem Resultados | Atualizar `\include` |
| `Pre_Textual/Resumo.tex` | Resumo PT | Menciona RAG, FT e Revit | **Reescrever** |
| `Pre_Textual/Abstract.tex` | Resumo EN | Idem | **Reescrever** |
| `Pre_Textual/Abreviaturas.tex` | Lista de abreviaturas | A revisar | Adicionar N1, N2, N3, EN1, EN2, EN1N2, SBERT, WMD, BERTimbau, TF-IDF |
| `Pre_Textual/Simbolos.tex` | Lista de símbolos | A revisar | Manter ou atualizar |
| `Conteudo/01_Introducao.tex` | Introdução | Completo (proposta) | **Editar conforme §1** |
| `Conteudo/03_Fundamentacao_Teorica.tex` | Fundamentação | Completo | **Editar conforme §2** |
| `Conteudo/04_Metodo.tex` | Proposta → Metodologia | Redigido como proposta | **Reescrever conforme §3** |
| `Conteudo/05_Resultados.tex` | Resultados | **Não existe** | **Criar conforme §4** |
| `Conteudo/06_Conclusao.tex` | Conclusão | Existe vazio como `05_Conclusao.tex` | **Renomear e redigir conforme §5** |

---

## 1. Introdução (`01_Introducao.tex`)

**Manter:** o panorama de BIM, AM, IA Generativa, LLMs e a apresentação da metodologia RASE.

**Reescrever a seção "Objetivos"** com o objetivo geral, objetivos específicos e a delimitação do que **não foi feito**.

### Objetivo geral (texto-base)

Avaliar comparativamente o uso de seis Modelos de Linguagem de Grande Porte (LLMs) *open-source* — Llama, Dolphin, Gemma, Mistral, Alpaca e Qwen — para a conversão automática de normas técnicas brasileiras da AEC (NBR 9050 e similares) em representações computáveis no formato RASE, utilizando exclusivamente Engenharia de Prompt em três níveis sucessivos de normalização (N1, N2, N3).

### Objetivos específicos (texto-base)

- Definir e implementar três níveis de normalização (N1 – segmentação atômica, N2 – identificação dos operadores RASE, N3 – estruturação semântica em JSON).
- Projetar prompts adequados a cada nível (Direct, Chain-of-Thought, Few-Shot).
- Comparar seis LLMs *open-source* sob três experimentos: EN1 (N1 isolado), EN2 (N2 isolado com N1 de referência) e EN1N2 (pipeline encadeado).
- Avaliar a qualidade das saídas com métricas de similaridade lexical (FuzzyWuzzy, TF-IDF), semântica (SBERT, BERTimbau, Multilingual) e de distância (WMD_ft, WMD_nilc), complementadas por métricas de classificação (Accuracy, Precision, Recall, F1-score).
- Analisar a propagação de erros entre as etapas do pipeline e o custo computacional (tempo) por modelo.

### Delimitação (a incluir)

Não fazem parte do escopo: aplicação dos resultados em software BIM (Revit/Dynamo); Fine-Tuning dos modelos; uso de RAG ou bancos vetoriais; treinamento de embeddings próprios; ampliação para normas internacionais.

### Organização do Documento (substitui "Organização da Proposta")

Renomear `\section{Organização da Proposta}` (linha 88 do `01_Introducao.tex`) para `\section{Organização do Documento}` e reescrever:

- **Capítulo 2 — Fundamentação Teórica:** BIM, AM, PLN, Redes Neurais (LSTM, BiLSTM, Transformers), LLM e a metodologia RASE.
- **Capítulo 3 — Metodologia:** níveis N1/N2/N3, técnicas de Engenharia de Prompt utilizadas, modelos LLM avaliados, dataset, pipeline e métricas.
- **Capítulo 4 — Resultados:** desempenho por modelo e por métrica nos experimentos EN1, EN2 e EN1N2; tempos de execução; análise comparativa.
- **Capítulo 5 — Conclusão:** síntese, limitações e trabalhos futuros.

### Edições específicas

- [ ] Substituir **R1/R2/R3 → N1/N2/N3** em todas as ocorrências (parágrafos sobre os modelos e exemplos).
- [ ] Remover a frase sobre marcação de elementos no Revit em **verde/vermelho/azul**.
- [ ] Remover **EPFT, EPRAG, EPFTRAG** — manter apenas EP.
- [ ] Remover a Figura comentada `Imagens/1.1.1-metodologia.png` (pertence à pipeline com Revit).

---

## 2. Fundamentação Teórica (`03_Fundamentacao_Teorica.tex`)

**Manter** as 8 seções (BIM, AM, PLN, RNAs, LSTM, Transformers, LLM, RASE) + Trabalhos Relacionados.

### Edições específicas

- [ ] **Seção 2.7 LLM:** **remover toda a discussão sobre RAG** (parágrafos sobre pesquisa vetorial, similaridade vetorial, re-ranking, PostgresVector, Figura 3.7.1 e citações `lewis2021`, `akkiraju2024`, `izacard2021`, `manning2008`, `mikolov2013a`). RAG não foi utilizado e não deve aparecer na fundamentação.
- [ ] **Seção 2.7 LLM:** manter a discussão sobre Engenharia de Prompt e suas variantes (Direct, Chain-of-Thought, Few-Shot). Garantir que o texto reforce essas três técnicas, pois serão referenciadas no Capítulo 3.
- [ ] **Seção 2.2 Aprendizado de Máquina:** confirmar que estão presentes as definições de Acurácia, Precisão, Revocação e F1 (já existem nas linhas 65–115). Servirão de base teórica para as métricas de classificação adicionadas no Capítulo 4.
- [ ] **Adicionar uma subseção curta sobre métricas de similaridade textual em PLN** (após seção 2.3 PLN ou dentro dela): FuzzyWuzzy (Levenshtein parcial), TF-IDF + cosseno, *sentence embeddings* com SBERT/BERTimbau/Multilingual, e Word Mover's Distance. Essas métricas aparecem nos Resultados e precisam de fundamento teórico.
- [ ] **Trabalhos Relacionados:** revisar para deixar claro o **diferencial** da pesquisa: comparação sistemática entre 6 LLMs *open-source* via Ollama, exclusivamente com Engenharia de Prompt, em três níveis de normalização, com avaliação multimétrica.

---

## 3. Metodologia (`04_Metodo.tex` — atualmente "Proposta")

> **Renomear** `\chapter{Proposta}` → `\chapter{Metodologia}`.
>
> **Reescrever todo o capítulo no tempo pretérito/presente descritivo** ("foi feito", "obteve-se", "implementou-se"). O trabalho **já foi executado**.
>
> **Renomear R1/R2/R3 → N1/N2/N3** em todas as ocorrências.
>
> **Remover completamente** as abordagens EPFT, EPRAG, EPFTRAG, PostgresVector, hiperparâmetros de fine-tuning, Dynamo, Revit, marcação colorida e planilha de auditoria.

### Estrutura sugerida do novo capítulo

```
3.   Metodologia
3.1  Visão Geral
3.2  Necessidade de Normalização em Três Níveis
     3.2.1 N1 — Segmentação Atômica
     3.2.2 N2 — Identificação dos Operadores RASE
     3.2.3 N3 — Estruturação Semântica em JSON
3.3  Engenharia de Prompt
     3.3.1 Prompt Direct
     3.3.2 Prompt Chain-of-Thought
     3.3.3 Prompt Few-Shot
3.4  Modelos LLM Avaliados
3.5  Dataset
3.6  Pipeline de Execução e Experimentos
     3.6.1 Experimento EN1
     3.6.2 Experimento EN2
     3.6.3 Experimento EN1N2
3.7  Métricas de Validação
     3.7.1 Métricas de Similaridade Lexical
     3.7.2 Métricas de Similaridade Semântica
     3.7.3 Métricas de Distância (WMD)
     3.7.4 Métricas de Classificação
3.8  Ambiente Computacional
```

### 3.1 Visão Geral

Esta pesquisa avaliou o uso de LLMs *open-source* para converter normas técnicas da AEC em representações computáveis no formato RASE, utilizando **exclusivamente Engenharia de Prompt** (sem Fine-Tuning, sem RAG e sem banco vetorial). A conversão foi modelada como um processo de **normalização em três níveis sucessivos** (N1 → N2 → N3). Seis modelos LLM *open-source* foram avaliados sob três experimentos (EN1, EN2, EN1N2), em um dataset com 79 normas brasileiras anotadas, e comparados por dez métricas (seis de similaridade textual e quatro de classificação).

### 3.2 Necessidade de Normalização em Três Níveis

> **Seção central** que justifica a decomposição da tarefa.

**Objetivo geral leve.** A cada chamada ao LLM, pede-se uma transformação pequena e bem delimitada. **Necessidade de chegar lá.** A transformação completa (texto bruto → JSON RASE final) feita em uma única chamada mistura raciocínios distintos (segmentação, classificação semântica e extração de atributos) que degradam a qualidade quando solicitados em conjunto.

**Por que três níveis e não um.** Em testes preliminares, pedir o JSON RASE diretamente produziu alucinações, omissões e estruturas inválidas. A decomposição em três níveis isola cada decisão e permite validar cada etapa independentemente.

#### 3.2.1 N1 — Segmentação Atômica

- **Problema:** uma sentença normativa frequentemente contém múltiplas regras coordenadas (ex.: "A inclinação transversal deve ser de até 2% para pisos internos e 3% para pisos externos" → duas regras).
- **Necessidade:** sem segmentar, os níveis seguintes não conseguem aplicar operadores RASE corretamente.
- **Implementação:** `generates/generate_n1.py` + `prompts/n1.txt`.
- **Entrada:** texto bruto (`text`) de `dataset.json`.
- **Saída:** `texts_n1` — lista de sentenças atômicas.
- **Exemplo de prompt** (de `prompts/n1.txt`): instrui o modelo a quebrar em sentenças curtas e diretas, uma regra computável por sentença, sem inventar elementos. Inclui um exemplo demonstrativo.

#### 3.2.2 N2 — Identificação dos Operadores RASE

- **Problema:** dada uma regra atômica, identificar quais trechos correspondem a Requisito (R), Aplicabilidade (A), Seleção (S) e Exceção (E).
- **Necessidade:** essa classificação é o cerne da metodologia RASE; sem ela, o texto continua em linguagem natural.
- **Implementação:** `generates/generate_n2.py` + `prompts/n2.txt`.
- **Entrada:** regras N1 (do dataset em EN2; do modelo em EN1N2).
- **Saída:** para cada regra N1, os campos `aplicabilidade`, `selecao`, `execao`, `requisito` em `operators_n2`.
- **Características do prompt:** ordem fixa dos quatro operadores, formato exato de saída em 4 linhas, marcação de campo vazio com `""`, exemplo único embutido.

#### 3.2.3 N3 — Estruturação Semântica em JSON

- **Problema:** mesmo após classificar como R/A/S/E, o trecho continua em linguagem natural; um verificador automático precisa do tripé estruturado *objeto · propriedade · valor* (com comparador e unidade).
- **Necessidade:** este passo torna a regra computável e comparável contra um modelo BIM.
- **Implementação:** `generates/generate_n3.py` + **um prompt por operador** (`prompts/n3_aplicabilidade.txt`, `n3_requisito.txt`, `n3_selecao.txt`, `n3_execao.txt`). Foi necessário um prompt por tipo de operador porque cada um demanda raciocínio distinto (Aplicabilidade descreve *a quem se aplica*; Requisito descreve *o que é exigido*; etc.).
- **Entrada:** operadores N2 (`text_n2` por operador).
- **Saída:** `properties_n3` em JSON com `type`, `object`, `property`, `comparation`, `target`, `unit`.
- **Características dos prompts:** schema JSON explícito, regras heurísticas de mapeamento por padrões textuais comuns (ex.: "uso público" → `property "uso", comparation "=", target "público"`), múltiplos exemplos few-shot por operador.

**Pipelines compostos.** Implementados em `generates/generate_n1n2.py` e `generates/generate_n1n2n3.py` para avaliar a propagação de erros (experimento EN1N2 e o pipeline completo).

### 3.3 Engenharia de Prompt

> **Cada técnica em sua própria subseção.**

A pesquisa utilizou **exclusivamente Engenharia de Prompt** como abordagem. Não houve Fine-Tuning nem RAG. Toda a especialização foi feita pelo desenho dos prompts em `prompts/`. As três técnicas foram aplicadas conforme a natureza de cada nível.

#### 3.3.1 Prompt Direct

- **Descrição:** instrução direta e objetiva, sem encadeamento de raciocínio explícito.
- **Aplicação:** **N1** — segmentar uma sentença em sub-regras é estruturalmente simples e não exige raciocínio sobre semântica normativa profunda.
- **Vantagem:** menor consumo de tokens e menor latência.
- **Risco:** baixa robustez quando a sentença é longa ou ambígua.
- **Evidência no código:** `prompts/n1.txt` consiste em 5 regras imperativas + 1 exemplo curto, sem instruções de raciocínio passo a passo.

#### 3.3.2 Prompt Chain-of-Thought

- **Descrição:** o prompt instrui o LLM a explicitar raciocínio em etapas antes da resposta final.
- **Aplicação:** **N2** — classificar trechos como R/A/S/E exige interpretação do papel sintático-semântico dentro da regra.
- **Vantagem:** reduz alucinações e classifica melhor sentenças com múltiplos operadores.
- **Risco:** maior consumo de tokens.
- **Evidência no código:** `prompts/n2.txt` apresenta a ordem fixa dos passos (1. aplicabilidade → 2. seleção → 3. exceção → 4. requisito), guiando o modelo por uma cadeia de decisão.

#### 3.3.3 Prompt Few-Shot

- **Descrição:** o prompt inclui exemplos completos de entrada → saída, ancorando o formato esperado.
- **Aplicação:** **N3** — a saída precisa seguir um esquema JSON rígido; sem exemplos, os modelos divergem do formato.
- **Vantagem:** alta aderência ao formato e à terminologia esperada.
- **Risco:** os exemplos consomem janela de contexto.
- **Evidência no código:** `prompts/n3_*.txt` trazem 2 a 4 exemplos completos cada (`Operador N2 → JSON`).

### 3.4 Modelos LLM Avaliados

Seis modelos *open-source* servidos localmente via **Ollama** (`ollama serve`):

| Modelo | Origem | Notas |
|---|---|---|
| Llama | Meta | Modelo de referência, maior latência observada |
| Dolphin | Cognitive Computations | Variante alinhada por instruções |
| Gemma | Google | Modelo compacto |
| Mistral | Mistral AI | LLM eficiente em parâmetros |
| Alpaca | Stanford | Variante Llama instruída |
| Qwen | Alibaba | LLM multilíngue |

Todos executados no mesmo hardware, com os mesmos prompts e o mesmo dataset, garantindo comparabilidade direta.

### 3.5 Dataset

- **Arquivo único:** `mestrado-rase/dataset.json`.
- **Tamanho:** 79 normas (`counts: 79`), aproximadamente 270 KB.
- **Origem:** normas brasileiras AEC, em especial NBR 9050 (acessibilidade), adaptadas do trabalho de Eduardo (2020).
- **Estrutura por entrada:**
  - `text`: texto bruto da norma.
  - `texts_n1`: lista, cada item com `text_n1` e `operators_n2`.
  - `operators_n2`: dicionário com chaves `requeriments`, `aplicability`, `selection`, `exception`, cada uma com `text_n2` e `properties_n3`.
  - `properties_n3`: JSON com `type`, `object`, `property`, `comparation`, `target`, `unit`.
- **Uso duplo:** mesmo arquivo serve como entrada para os geradores e como `target` de referência para os validadores.

### 3.6 Pipeline de Execução e Experimentos

Orquestração: `main.py` → `generates/menu_generate.py` (geração) e `validates/menu_validate.py` (validação). Saídas geradas em `predicts/generate_<nivel>_<modelo>.json`; resultados de validação em `metrics/validate_<nivel>.json`.

#### 3.6.1 Experimento EN1

Avalia a geração N1 isoladamente. Entrada: `text` do dataset. Comparação: `text_n1` gerado × `text_n1` real. Mede a qualidade da segmentação a partir do texto bruto.

#### 3.6.2 Experimento EN2

Avalia a geração N2 isoladamente, eliminando ruído upstream. Entrada: `text_n1` do dataset. Comparação: `text_n2` gerado × `text_n2` real, por operador (R, A, S, E). Mede a qualidade pura da classificação RASE.

#### 3.6.3 Experimento EN1N2

Pipeline encadeado em que o N1 gerado pelo modelo alimenta a etapa N2. Avalia a **propagação de erros** entre os níveis. Saída comparada ao `text_n2` real.

### 3.7 Métricas de Validação

#### 3.7.1 Similaridade Lexical

- **FuzzyWuzzy** (`fuzz.partial_ratio`): similaridade parcial baseada em distância de Levenshtein.
- **TF-IDF**: cosseno entre vetores TF-IDF das duas strings.

#### 3.7.2 Similaridade Semântica

- **SBERT (PT)**: `tgsc/sentence-transformer-ult5-pt-small`.
- **BERTimbau**: `rufimelo/Legal-BERTimbau-sts-large-ma-v3` — *embeddings* especializados em texto jurídico em português.
- **Multilingual**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`.

#### 3.7.3 Distância Semântica (WMD)

- **WMD_ft**: Word Mover's Distance com FastText (`fasttext-wiki-news-subwords-300`).
- **WMD_nilc**: WMD com embeddings NILC (`cbow_s300.txt`), normalizado para [0,1].

#### 3.7.4 Métricas de Classificação (a adicionar)

> **A implementar.** Atualmente ausentes em `validates/`. Definir via limiar sobre similaridade semântica (ex.: SBERT ≥ 0,7 → acerto) ou via correspondência exata por operador no caso de N2/N3.
>
> - **Accuracy** = (TP + TN) / (TP + TN + FP + FN)
> - **Precision** = TP / (TP + FP)
> - **Recall** = TP / (TP + FN)
> - **F1-score** = 2 · (Precision · Recall) / (Precision + Recall)
>
> Persistir as quatro novas métricas ao lado das já existentes em `metrics/validate_*.json`. Atualizar `averages` para incluí-las.

### 3.8 Ambiente Computacional

Hardware da execução (de `mestrado-rase/resultados_llama.md`):

- **CPU:** 13th Gen Intel Core i9-13900K (3.00 GHz)
- **RAM:** 32 GB
- **GPU:** NVIDIA RTX 4080
- **SO:** Ubuntu 22.04
- **Python:** 3.11.9
- **Servidor LLM:** Ollama (`ollama serve`)
- **Bibliotecas principais:** `sentence-transformers`, `gensim`, `fuzzywuzzy`, `sklearn` (TF-IDF)

### Edições específicas no `04_Metodo.tex`

- [ ] Renomear `\chapter{Proposta}` → `\chapter{Metodologia}`.
- [ ] Reescrever no tempo pretérito.
- [ ] Renomear R1/R2/R3 → N1/N2/N3 em todas as ocorrências.
- [ ] Remover EPFT, EPRAG, EPFTRAG, PostgresVector, hiperparâmetros de FT, Dynamo, Revit, marcação colorida.
- [ ] Adicionar a seção 3.2 (Necessidade de Normalização) e a seção 3.3 (Engenharia de Prompt em três subseções).
- [ ] Substituir lista de modelos por: Llama, Dolphin, Gemma, Mistral, Alpaca, Qwen via Ollama.
- [ ] Substituir métricas atuais pelas reais: FuzzyWuzzy, TF-IDF, SBERT, BERTimbau, Multilingual, WMD_ft, WMD_nilc + Accuracy, Precision, Recall, F1.
- [ ] Remover seções "Desenvolvimento Inicial", "Desafios Futuros" e "Fases da projeto e cronograma" — não cabem em capítulo retrospectivo. O que houver de aprendizado migra para Conclusão (§5).
- [ ] Remover Figura `Imagens/4.1.1-cronograma.png`.

---

## 4. Resultados (criar `Conteudo/05_Resultados.tex`)

> **Capítulo novo.** Conteúdo-base já consolidado em `mestrado-rase/resultados.md` e `mestrado-rase/resultados_llama.md`. Converter para LaTeX no novo arquivo.

### Estrutura sugerida

```
4.   Resultados
4.1  Visão Geral dos Experimentos
4.2  Resultados por Experimento
     4.2.1 EN1 — Segmentação N1
     4.2.2 EN2 — Identificação RASE
     4.2.3 EN1N2 — Pipeline Encadeado
4.3  Resultados por Modelo
     4.3.1 Llama
     4.3.2 Dolphin
     4.3.3 Gemma
     4.3.4 Mistral
     4.3.5 Alpaca
     4.3.6 Qwen
4.4  Análise por Métrica
     4.4.1 Lexicais (FuzzyWuzzy, TF-IDF)
     4.4.2 Semânticas (SBERT, BERTimbau, Multilingual)
     4.4.3 Distância (WMD_ft, WMD_nilc)
     4.4.4 Classificação (Accuracy, Precision, Recall, F1)
4.5  Análise de Tempo de Execução
4.6  Discussão Integrada
```

### 4.1 Visão Geral dos Experimentos

Apresentar a Tabela de médias por métrica nos três experimentos (já em `resultados.md`):

| Experimento | FuzzyWuzzy | TF-IDF | SBERT | Multilingual | WMD_ft | WMD_nilc |
|---|---|---|---|---|---|---|
| EN1 | 0,638 | 0,460 | 0,710 | 0,749 | 0,661 | 0,659 |
| EN2 | 0,528 | 0,462 | 0,587 | 0,668 | 0,694 | 0,655 |
| EN1N2 | 0,502 | 0,360 | 0,567 | 0,650 | 0,628 | 0,608 |

> **Observação:** essa tabela atualmente não inclui BERTimbau (validação foi rodada com BERTimbau em `resultados_llama.md`). Recalcular médias agregadas incluindo BERTimbau para o capítulo final.

### 4.2 Resultados por Experimento

#### 4.2.1 EN1

- Métricas semânticas (SBERT 0,710 e Multilingual 0,749) > lexicais (TF-IDF 0,460; FuzzyWuzzy 0,638).
- **Líder em métricas semânticas e WMD:** Dolphin (SBERT 0,840; Multilingual 0,873; WMD_ft 0,748; WMD_nilc 0,740).
- **Líder em FuzzyWuzzy:** Gemma (0,724).
- Justificativa: a tarefa de segmentação tolera reformulações lexicais; modelos que parafraseiam bem mantêm semântica.

#### 4.2.2 EN2

- Médias inferiores ao EN1 (SBERT 0,587; Multilingual 0,668), evidenciando dificuldade em formalização estruturada.
- **Líder absoluto:** Llama (Multilingual 0,869; WMD_ft 0,857; SBERT 0,806; FuzzyWuzzy 0,761; TF-IDF 0,777; WMD_nilc 0,806).
- WMD > TF-IDF e FuzzyWuzzy → robustez a variações de superfície.

#### 4.2.3 EN1N2

- Degradação consistente em relação ao EN2 (TF-IDF 0,360; SBERT 0,567; Multilingual 0,650), confirmando propagação de erros.
- **Líder em semânticas:** Llama (SBERT 0,678; Multilingual 0,743).
- **Líder em TF-IDF e WMD:** Dolphin (TF-IDF 0,506; WMD_ft 0,692; WMD_nilc 0,669).
- Perfis complementares no cenário encadeado.

### 4.3 Resultados por Modelo

Subseção por modelo com seus números nos três experimentos. Conteúdo já no `resultados.md` (linhas 43–48). Para o Llama, usar a discussão expandida do `resultados_llama.md`, incluindo a linha BERTimbau (EN1: 0,773 / EN2: 0,851 / EN1N2: 0,719).

**Ranking global** (média de todas as métricas e experimentos):

1. Llama — 0,716
2. Dolphin — 0,676
3. Mistral — 0,656
4. Gemma — n/d (calcular)
5. Alpaca — 0,477
6. Qwen — 0,433

### 4.4 Análise por Métrica

- **Lexicais:** quedas progressivas de EN1 → EN1N2 (FuzzyWuzzy 0,638 → 0,502; TF-IDF 0,460 → 0,360); penalizam reformulações.
- **Semânticas:** mais estáveis; SBERT/Multilingual capturam equivalência mesmo com paráfrases.
- **WMD:** desempenho intermediário; sensíveis à estruturação de operadores.
- **Classificação (a calcular):** após implementar Accuracy/Precision/Recall/F1, incluir tabela com TP/FP/FN/TN por modelo e experimento.

### 4.5 Tempo de Execução

Tabelas já presentes em `resultados.md` (linhas 110–162):

- **N1:** Llama é o mais lento (1h34min); Dolphin o mais rápido (62s).
- **N2:** Llama (1h54min) e Qwen (1h48min) são os mais lentos.
- **N1N2:** Qwen (2h48min) e Llama (2h37min) são os mais lentos; Dolphin permanece rápido (1m44s).

Discutir o trade-off entre qualidade e custo computacional (Llama lidera qualidade mas com tempo 50× a 100× maior que os mais rápidos).

### 4.6 Discussão Integrada

- Embeddings semânticos (SBERT, BERTimbau, Multilingual) são as métricas mais adequadas para validar transformações normativas em LLMs.
- O pipeline encadeado (EN1N2) sofre degradação esperada por propagação; a robustez relativa das semânticas mostra que o significado é preservado mesmo quando a forma muda.
- Llama é o melhor para qualidade global; Dolphin oferece o melhor *custo-benefício* (qualidade competitiva com tempo muito menor).
- Qwen e Alpaca são os mais fracos consistentemente — não recomendados para a tarefa.

### Edições / Criação

- [ ] Criar `Conteudo/05_Resultados.tex` com `\chapter{Resultados}` + as seções acima.
- [ ] Migrar tabelas de `resultados.md` para o LaTeX (já estão em formato `tabular`).
- [ ] Recalcular médias com BERTimbau incluído após rerun completo.
- [ ] Adicionar Accuracy/Precision/Recall/F1 à tabela após implementar (§6).

---

## 5. Conclusão (`05_Conclusao.tex` → renomear para `06_Conclusao.tex`)

> Atualmente vazio. Redigir do zero.

### Estrutura sugerida

```
5.   Conclusão
5.1  Síntese dos Resultados
5.2  Contribuições
5.3  Limitações
5.4  Trabalhos Futuros
```

### 5.1 Síntese dos Resultados

- A decomposição em três níveis (N1/N2/N3) viabilizou a conversão de normas AEC em RASE com LLMs *open-source* sem necessidade de Fine-Tuning ou RAG.
- Engenharia de Prompt sozinha foi suficiente para atingir similaridade semântica > 0,80 no melhor cenário (Llama em EN2).
- Métricas semânticas (SBERT, BERTimbau, Multilingual) demonstraram-se mais adequadas que lexicais para validar transformações normativas.
- Llama liderou qualidade global; Dolphin ofereceu o melhor custo-benefício; Qwen e Alpaca tiveram desempenho insatisfatório.

### 5.2 Contribuições

- Definição operacional dos três níveis de normalização (N1/N2/N3) sobre a metodologia RASE.
- Comparação sistemática de seis LLMs *open-source* na tarefa de conversão de normas.
- Conjunto de prompts especializados por nível e por operador, disponível como artefato em `mestrado-rase/prompts/`.
- Pipeline reproduzível e dataset anotado de 79 normas brasileiras.

### 5.3 Limitações

- Dataset relativamente pequeno (79 normas), restrito a normas brasileiras de acessibilidade (NBR 9050 e similares).
- Avaliação não cobriu N3 com a mesma profundidade que N1 e N2.
- As métricas de classificação (Accuracy, Precision, Recall, F1) dependem de um limiar de similaridade arbitrário.
- Não houve aplicação prática em software BIM (validação fim-a-fim em projetos reais).
- Modelos rodaram em hardware único; não há análise de variância entre execuções.

### 5.4 Trabalhos Futuros

- **Aplicação em BIM:** integração ao Revit/Dynamo (escopo originalmente proposto, agora deslocado para trabalho futuro).
- **Fine-Tuning e RAG:** explorar como evolução natural da abordagem só por prompt.
- **Ampliação do dataset:** incluir mais normas brasileiras (NBRs estruturais, hidráulicas, elétricas) e normas internacionais.
- **Avaliação humana:** complementar as métricas automáticas com avaliação por especialistas AEC.
- **Estudo de variância:** múltiplas execuções por modelo e configurações de temperatura.

### Edições / Criação

- [ ] Renomear `Conteudo/05_Conclusao.tex` → `Conteudo/06_Conclusao.tex`.
- [ ] Redigir o capítulo conforme as quatro seções acima.

---

## 6. Pendências de código (`mestrado-rase/`)

A serem implementadas antes da escrita final do capítulo de Resultados.

### 6.1 Adicionar métricas de classificação

- Implementar **Accuracy**, **Precision**, **Recall** e **F1-score** em:
  - `validates/validate_n1.py`
  - `validates/validate_n2.py`
  - `validates/validate_n3.py`
  - `validates/validate_n1n2.py`
  - `validates/validate_n1n2n3.py`
- Definir o critério de "acerto":
  - **Opção A (recomendada para N1/N2):** limiar sobre SBERT ou Multilingual (ex.: similaridade ≥ 0,7 → TP).
  - **Opção B (recomendada para N3):** correspondência exata por campo do JSON (`object`, `property`, `comparation`, `target`, `unit`).
- Persistir as novas métricas em `metrics/validate_*.json` ao lado das existentes.
- Atualizar `averages` para incluir as novas métricas.

### 6.2 Atualizações no código existente

- [ ] Conferir se BERTimbau está integrado aos cinco validadores (atualmente confirmado em `validate_n1.py`).
- [ ] Re-executar todas as validações após implementar Accuracy/Precision/Recall/F1.
- [ ] Atualizar `mestrado-rase/README.md` para listar as novas métricas.
- [ ] Recalcular as tabelas de `resultados.md` incluindo BERTimbau e as métricas de classificação.

### 6.3 Validação N3

- A `metrics/` existem `validate_n1.json`, `validate_n2.json`, `validate_n1n2.json` mas **não há `validate_n3.json`**. Verificar se `validate_n3.py` foi executado para os 6 modelos e popular o capítulo de Resultados com esses dados.

---

## 7. Pré-Textuais (`Pre_Textual/`)

### 7.1 `Resumo.tex`

> **Reescrever completamente.** O atual menciona RAG, Fine-Tuning e Revit.

Pontos a incluir no novo Resumo:
- Adoção crescente do BIM e necessidade de automação de normas regulatórias.
- Metodologia RASE como ponte entre normas e BIM.
- LLMs *open-source* como solução acessível para interpretação automática.
- **O que foi feito:** comparação de 6 LLMs (Llama, Dolphin, Gemma, Mistral, Alpaca, Qwen) via Ollama, em 3 níveis de normalização (N1/N2/N3), sob 3 experimentos (EN1/EN2/EN1N2), apenas com Engenharia de Prompt.
- **Métricas:** seis de similaridade textual + quatro de classificação.
- **Principais resultados:** Llama lidera qualidade global; Dolphin lidera custo-benefício.
- **Palavras-chave:** Aprendizado de Máquina, PLN, LLM, BIM, RASE, Engenharia de Prompt.

### 7.2 `Abstract.tex`

> **Reescrever completamente.** Tradução fiel do novo Resumo.

### 7.3 `Abreviaturas.tex`

Adicionar / confirmar entradas para:

- AEC — Arquitetura, Engenharia e Construção
- AM — Aprendizado de Máquina
- BIM — Building Information Modeling
- BERT — Bidirectional Encoder Representations from Transformers
- EN1, EN2, EN1N2 — Experimentos da pesquisa
- F1 — F1-score
- IA — Inteligência Artificial
- IAG — IA Generativa
- JSON — JavaScript Object Notation
- LLM — Large Language Model
- N1, N2, N3 — Níveis de normalização
- NBR — Norma Brasileira
- PLN — Processamento de Linguagem Natural
- RASE — Requirement, Applicability, Selection, Exception
- RNA — Rede Neural Artificial
- SBERT — Sentence-BERT
- TF-IDF — Term Frequency–Inverse Document Frequency
- WMD — Word Mover's Distance

### 7.4 `Simbolos.tex`

- Manter ou atualizar conforme as fórmulas presentes (Acurácia, Precisão, Revocação, F1, Cosseno).

### Edições

- [ ] Reescrever `Resumo.tex`.
- [ ] Reescrever `Abstract.tex`.
- [ ] Atualizar `Abreviaturas.tex` com a lista acima.

---

## 8. Estrutura raiz (`Modelo-Mestrado-PROCC.tex`)

### 8.1 Atualizar `\include`

Atualmente (linhas 67–71):

```latex
\include{Conteudo/01_Introducao}
% \include{Conteudo/02_Trabalhos_Relacionados}
\include{Conteudo/03_Fundamentacao_Teorica}
\include{Conteudo/04_Metodo}
% \include{Conteudo/05_Conclusao}
```

Substituir por:

```latex
\include{Conteudo/01_Introducao}
\include{Conteudo/03_Fundamentacao_Teorica}
\include{Conteudo/04_Metodo}
\include{Conteudo/05_Resultados}
\include{Conteudo/06_Conclusao}
```

### 8.2 Verificar título da dissertação

Título atual (linha 36): "Análise de LLMs baseados LLaMA 3 para a Verificação Automática de Normas de Arquitetura, Engenharia e Construção".

Como a pesquisa usa **6 LLMs** (não apenas LLaMA 3) e **não realiza verificação automática em projetos** (apenas conversão), considerar reescrita:

- *"Análise Comparativa de LLMs Open-Source para a Conversão de Normas de Arquitetura, Engenharia e Construção em Representações RASE"*

### 8.3 Outros

- [ ] Remover `\usepackage{lipsum}` se não houver mais lipsum no texto final.
- [ ] Confirmar que `lstlisting` JSON está sendo usado nos exemplos do Capítulo 3 (já configurado, linhas 15–24).

---

## 9. Imagens e artefatos visuais

### 9.1 Imagens existentes a manter

- `3.1.1-bim.png` (BIM)
- `3.3.1-matrizconfusao.png` (Matriz de Confusão — relevante para Acurácia/Precisão/Revocação/F1)
- `3.4.1-rna.png`, `3.4.2-rnamlp.png`, `3.4.3-bias.png`, `3.4.4-tiposrna.png` (RNA)
- `3.5.1-token.png`, `3.5.2-stopwords.png`, `3.5.3-wordembeddings.png`, `3.5.4-sentenceembeddings.png` (PLN)
- `3.6.1-seq2seq.png` … `3.6.5-camadastransformer.png` (Transformers)
- `3.8.1-rase.png` (RASE)

### 9.2 Imagens a remover

- `1.1.1-metodologia.png` — pipeline com Revit, não cabe mais.
- `3.7.1-rag.png` — RAG removido da fundamentação.
- `4.1.1-cronograma.png` — cronograma da proposta.

### 9.3 Imagens a criar

- **Pipeline atualizado** (substitui `1.1.1-metodologia.png`): fluxo dataset → N1 → N2 → N3 → métricas, sem Revit.
- **Diagrama dos três experimentos** (EN1, EN2, EN1N2): caixas mostrando entrada/saída de cada um.
- **Gráficos de barras** comparando os 6 modelos por métrica em cada experimento (gerar via matplotlib a partir dos JSONs em `metrics/`).
- **Heatmap modelo × métrica** consolidado.

---

## 10. Bibliografia (`Bibliografia.bib`)

### 10.1 Citações a adicionar

- **SBERT:** Reimers & Gurevych (2019), *"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"*.
- **BERTimbau:** Souza, Nogueira & Lotufo (2020), *"BERTimbau: Pretrained BERT Models for Brazilian Portuguese"*.
- **WMD:** Kusner et al. (2015), *"From Word Embeddings to Document Distances"*.
- **FastText:** Bojanowski et al. (2017).
- **Ollama:** referência ao projeto.
- **NBR 9050** (ABNT) — norma de acessibilidade utilizada como base do dataset.

### 10.2 Citações a remover (se exclusivas a RAG/FT removidos)

- Verificar se `lewis2021`, `akkiraju2024`, `izacard2021`, `manning2008`, `mikolov2013a` ainda são referenciados após as edições da §2.7. Remover se ficarem órfãs.

---

## 11. Checklist consolidada

### `Modelo-Mestrado-PROCC.tex`
- [ ] Atualizar `\include` para incluir `05_Resultados` e `06_Conclusao`.
- [ ] Reavaliar título.

### `Pre_Textual/`
- [ ] Reescrever `Resumo.tex`.
- [ ] Reescrever `Abstract.tex`.
- [ ] Atualizar `Abreviaturas.tex`.

### `01_Introducao.tex`
- [ ] R1/R2/R3 → N1/N2/N3.
- [ ] Reescrever objetivo (§1).
- [ ] Remover Revit / verde-vermelho-azul / EPFT/EPRAG/EPFTRAG.
- [ ] Renomear seção para "Organização do Documento".
- [ ] Adicionar delimitação de escopo.

### `03_Fundamentacao_Teorica.tex`
- [ ] Remover discussão de RAG da seção 2.7 LLM.
- [ ] Confirmar presença de Acurácia/Precisão/Revocação/F1 em 2.2.
- [ ] Adicionar subseção sobre métricas de similaridade textual.
- [ ] Atualizar Trabalhos Relacionados para destacar diferencial.

### `04_Metodo.tex`
- [ ] Renomear capítulo para Metodologia.
- [ ] Reescrever em pretérito.
- [ ] R1/R2/R3 → N1/N2/N3.
- [ ] Remover EPFT, EPRAG, EPFTRAG, PostgresVector, Dynamo, Revit.
- [ ] Adicionar seção 3.2 (Necessidade de Normalização).
- [ ] Adicionar seção 3.3 com subseções 3.3.1/3.3.2/3.3.3.
- [ ] Substituir lista de modelos (6 LLMs via Ollama).
- [ ] Substituir métricas (incluir BERTimbau + Accuracy/Precision/Recall/F1).
- [ ] Remover seções "Desenvolvimento Inicial", "Desafios Futuros", "Cronograma".
- [ ] Adicionar seção de Ambiente Computacional.

### `05_Resultados.tex` (criar)
- [ ] Criar arquivo novo.
- [ ] Migrar tabelas de `resultados.md`.
- [ ] Recalcular médias incluindo BERTimbau.
- [ ] Incluir métricas de classificação após implementação.
- [ ] Adicionar gráficos comparativos.

### `06_Conclusao.tex` (renomear de `05_Conclusao.tex`)
- [ ] Renomear arquivo.
- [ ] Redigir Síntese, Contribuições, Limitações, Trabalhos Futuros.

### `mestrado-rase/`
- [ ] Implementar Accuracy/Precision/Recall/F1 nos validadores.
- [ ] Re-executar validações.
- [ ] Confirmar `validate_n3.json` para os 6 modelos.
- [ ] Atualizar README.

### `Bibliografia.bib`
- [ ] Adicionar SBERT, BERTimbau, WMD, FastText, Ollama, NBR 9050.
- [ ] Remover citações órfãs de RAG.

### `Imagens/`
- [ ] Remover `1.1.1-metodologia.png`, `3.7.1-rag.png`, `4.1.1-cronograma.png`.
- [ ] Criar pipeline atualizado, diagrama de experimentos, gráficos comparativos.
