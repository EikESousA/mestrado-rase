# Verificação de Citações

Este documento lista as citações da dissertação cujo conteúdo da referência **não corresponde** (ou corresponde de forma muito frágil) à afirmação feita no texto. Para cada caso, sugere-se uma referência alternativa **já presente em `dissertacao/Bibliografia.bib`** que sustenta melhor a afirmação.

A verificação foi feita confrontando o trecho do texto com o título/escopo real da publicação citada (confirmado, quando possível, por busca pública na fonte original).

---

## 1. `\cite{monteiro2011}` — origem do BIM a partir do CAD 3D paramétrico

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:8`

**Trecho:**
> *"Esse recurso surgiu \"após a inovação do CAD 3D paramétrico\", tecnologia que foi amplamente adotada em setores como aeroespacial, automotivo e de manufatura \cite{monteiro2011}."*

**Problema:** A dissertação de Ari Monteiro (USP, 2011) intitula-se **"Projeto para a produção de vedações verticais em alvenaria em uma ferramenta CAD-BIM"** e trata de modelagem/representação de modulação de alvenaria em ferramentas BIM. Ela **não discute** a origem histórica do BIM a partir do CAD 3D paramétrico nem sua adoção em setores aeroespacial, automotivo e de manufatura.

**Alternativa sugerida (já no `.bib`):** `\cite{eastman2011}` — *BIM Handbook*, capítulo introdutório, discute explicitamente a evolução do CAD paramétrico e a sua adoção em manufatura/aeroespacial/automotivo antes da chegada ao AEC. Em segunda opção, `\cite{ibrahim2004}` (*Two Approaches to BIM: A Comparative Study*) também trata da transição CAD→BIM.

---

## 2. `\cite{arroyo2000}` — definição/aplicações de Aprendizado Profundo

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:130`

**Trecho:**
> *"Finalmente, o Aprendizado Profundo (Deep Learning) é uma técnica avançada de AM que utiliza redes neurais profundas, inspiradas nos neurônios do cérebro humano. (...) é amplamente utilizado em aplicações como reconhecimento de imagens, processamento de linguagem natural e sistemas de recomendação \cite{arroyo2000}"*

**Problema:** Arroyo-Figueroa et al. (2000) é **"Fuzzy intelligent system for the operation of fossil power plants"**, um trabalho sobre **sistemas fuzzy** aplicados à operação de usinas termoelétricas. **Não trata de Deep Learning** — Deep Learning como termo/área sequer estava consolidado em 2000.

**Alternativa sugerida (já no `.bib`):** `\cite{goodfellow2016}` (*Deep Learning*, MIT Press) ou `\cite{schmidhuber2015}` (*Deep learning in neural networks: An overview*) — ambos cobrem exatamente as aplicações citadas (visão, PLN, recomendação). `\cite{yann2015}` (*Deep Learning*, Nature) é uma terceira alternativa canônica.

---

## 3. `\cite{inan2023}` — definição/classificação dos LLMs

**Arquivo:** `dissertacao/Conteudo/01_Introducao.tex:19`

**Trecho:**
> *"Esses algoritmos são projetados para produzir respostas contextualmente sensíveis em linguagem humana e são classificados como LLMs \cite{inan2023}."*

**Problema:** Inan et al. (2023) é **"Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations"**, um artigo sobre **moderação/segurança** de entrada e saída de LLMs. **Não define nem classifica LLMs**; pressupõe a sua existência para propor um guardrail.

**Alternativa sugerida (já no `.bib`):** `\cite{zhao2023}` (*A Survey of Large Language Models*) — survey que define e classifica LLMs explicitamente. `\cite{naveed2024}` (*A Comprehensive Overview of Large Language Models*) é igualmente apropriada.

---

## 4. `\cite{du2024}` — uso de LLMs para interpretar normas regulatórias na AEC

**Arquivo:** `dissertacao/Conteudo/01_Introducao.tex:25`

**Trecho:**
> *"No setor de Arquitetura, Engenharia e Construção (AEC), os Modelos de Linguagem de Grande Escala (LLMs) podem auxiliar na interpretação de normas regulatórias e na conversão dessas informações em formatos processáveis por máquinas \cite{du2024}."*

**Problema:** Du, Nousias & Borrmann (2024) é **"Towards a Copilot in BIM Authoring Tool Using a Large Language Model-Based Agent for Intelligent Human-Machine Interaction"**. O artigo trata de um **copiloto/agente para uma ferramenta de autoria BIM (Vectorworks)**, automatizando tarefas de modelagem e interação humano-máquina. **Não trata** de interpretação de normas regulatórias nem da sua conversão em formatos processáveis.

**Alternativa sugerida (já no `.bib`):** `\cite{fuchs2024}` (*Using Large Language Models for the Interpretation of Building Regulations*) — exatamente o tema do trecho. A citação correta inclusive já aparece no parágrafo seguinte (linha 25) do mesmo arquivo. Recomenda-se substituir `\cite{du2024}` por `\cite{fuchs2024}` neste ponto.

---

## 5. `\cite{vargas2023}` — variabilidade regional de normas regulatórias

**Arquivos e trechos:**

- `dissertacao/Conteudo/01_Introducao.tex:17`:
  > *"... uma vez que essas normas são reguladas por região. Cada região possui suas próprias regras, muitas das quais são interpretativas, dificultando a automação desse processo \cite{vargas2023}."*

- `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:47`:
  > *"... as normas variam entre regiões e contextos, o que limita o reaproveitamento de regras já formalizadas em outros países \cite{vargas2023}."*

**Problema:** Vargas (*Análise da produção científica brasileira sobre a Modelagem da Informação da Construção*) é um estudo **bibliométrico** sobre a produção científica brasileira em BIM (originalmente publicado em 2017, na revista *Ambiente Construído*; a entrada do `.bib` aponta para 2023, o que também merece revisão). O artigo **não discute** variabilidade regional de normas técnicas nem o impacto disso na automação da verificação.

**Alternativa sugerida (já no `.bib`):** `\cite{dimyadi2013}` (*Automated building code compliance checking — where is it at?*) ou `\cite{solihin2015}` (*Classification of rules for automated BIM rule checking development*) — ambos discutem exatamente a heterogeneidade regional/jurisdicional das normas e seu efeito sobre a verificação automática. `\cite{eastman2009}` (*Automatic rule-based checking of building designs*) também cobre o ponto.

---

## 6. `\cite{fuchs2024}` (uso isolado) — IA transformando processos da Engenharia Civil

**Arquivo:** `dissertacao/Conteudo/01_Introducao.tex:13`

**Trecho:**
> *"No campo da Engenharia Civil, a IA tem transformado processos tradicionais em abordagens automatizadas, promovendo maior eficiência, precisão e sustentabilidade. Algoritmos de aprendizado de máquina, redes neurais e aprendizado profundo permitem que sistemas revisem e otimizem projetos desde a fase de planejamento até a execução de grandes obras \cite{fuchs2024}."*

**Problema:** Fuchs et al. (2024) é **especificamente sobre o uso de LLMs para interpretar regulamentos de construção** — escopo bem mais estreito do que "IA transformando a Engenharia Civil desde planejamento até execução". A citação é uma extrapolação do escopo real do artigo.

**Alternativa sugerida (já no `.bib`):** Para uma visão ampla de IA/AM na Engenharia Civil/AEC, combinar `\cite{rane2023}` (*Integrating BIM with ChatGPT, Bard, and similar generative AI in AEC*) com `\cite{liu2022}` (*BIM Machine Learning and Design Rules to Improve the Assembly Process*) — ambos cobrem o uso de AM/IA em projeto e execução. `\cite{samsami2024}` é uma terceira opção que discute amplamente IA generativa no setor AEC.

---

## 7. `\cite{devlin2019}` — modelos de word/sentence embeddings (Word2Vec, GloVe, fastText)

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:209`

**Trecho:**
> *"No contexto do PLN moderno, representações vetoriais, como word embeddings e sentence embeddings, têm sido amplamente utilizadas. Modelos como Word2Vec, GloVe, fastText e OpenAIEmbeddings destacam-se no campo \cite{devlin2019}."*

**Problema:** Devlin et al. (2019) é o **artigo do BERT** (*BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*). O artigo não apresenta nem catalogou Word2Vec, GloVe ou fastText — propõe um modelo distinto (BERT/Transformer).

**Alternativa sugerida (já no `.bib`):** Para a frase como está, o ideal é citar diretamente cada modelo: `\cite{mikolov2013a}` ou `\cite{mikolov2013b}` para Word2Vec, `\cite{pennington2014}` para GloVe e `\cite{bojanowski2017}` ou `\cite{joulin2016}` para fastText. Se for desejado um único panorama, `\cite{martin2009}` (Speech and Language Processing) cobre o tema de embeddings de forma geral.

---

## 8. `\cite{minsky1969}` — proposição do Perceptron Multicamadas (MLP)

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:239`

**Trecho:**
> *"... uma rede perceptron de três camadas é limitada a encontrar uma única solução. Para resolver problemas que exigem múltiplas soluções, Minsky e Papert propuseram a inclusão de múltiplas camadas intermediárias, resultando no modelo conhecido como perceptron multicamadas (Multi-layer Perceptron – MLP) \cite{minsky1969}."*

**Problema:** O livro *Perceptrons: An Introduction to Computational Geometry* (Minsky & Papert, 1969) **não propõe o MLP**. Pelo contrário, demonstra as **limitações** do perceptron de camada única (em particular, a impossibilidade de resolver o XOR) e essa demonstração contribuiu para o "inverno da IA". O treino prático de MLPs só viabilizou‑se depois, com a popularização do algoritmo de retropropagação por Rumelhart, Hinton & Williams (1986).

**Alternativa sugerida (já no `.bib`):** `\cite{rumelhart1986}` (*Learning Representations by Back-propagating Errors*) — para a viabilização do MLP via backpropagation. Para a descrição estrutural do MLP, `\cite{haykin1999}` ou `\cite{haykin2001}` (livros-texto de Redes Neurais) também são adequados. Pode-se manter `\cite{minsky1969}` se o texto for reescrito para indicar que esse trabalho *expôs as limitações do perceptron simples*, motivando posteriormente o MLP.

---

## 9. `\cite{zhang2024}` — recomendações de design de prompts (prompts curtos para LLaMa)

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:609-611`

**Trecho:**
> *"... Zhang afirma que, para modelos LLaMa, os prompts devem ser mantidos pequenos e simples para um melhor entendimento da tarefa \cite{zhang2024}. Prompts muito longos podem fazer com que os modelos percam informações relevantes. Além disso, a quantidade de amostras fornecidas como exemplos influencia diretamente na qualidade da extração ... \cite{zhang2024}."*

**Problema:** Zhang et al. (2024) é **"LLaMA-Adapter: Efficient Fine-tuning of Language Models with Zero-init Attention"**. O artigo trata de um **mecanismo de fine-tuning eficiente** (atenção com inicialização zero, prompts de adaptação treináveis) — **não** é uma diretriz de como escrever prompts curtos/simples para LLaMA em uso prático.

**Alternativa sugerida (já no `.bib`):** `\cite{brown2020}` (*Language Models are Few-Shot Learners* — GPT-3) discute diretamente o impacto do tamanho e da quantidade de exemplos no prompt. `\cite{nascimento2024}` (técnicas de engenharia de prompt) e `\cite{samsami2024}` (engenharia de prompts no AEC) também são apropriadas para recomendações práticas de design de prompts.

---

## 10. `\cite{sensoy2018}` — definição da função Softmax como ativação para classificação multiclasse

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:306`

**Trecho:**
> *"Função Softmax: É uma extensão da Sigmoid, projetada para problemas de classificação com múltiplas classes. Transforma as saídas de cada classe em valores entre 0 e 1, normalizando-as para que sua soma seja igual a 1. Assim, é possível interpretar os resultados como probabilidades de pertencimento a cada classe \cite{sensoy2018}."*

**Problema:** Sensoy, Kaplan & Kandemir (2018) — *Evidential Deep Learning to Quantify Classification Uncertainty* — na verdade **critica** o uso de Softmax como estimador de probabilidade e propõe uma alternativa baseada em teoria da evidência (Dirichlet). Citá-lo como definição padrão da função Softmax inverte a tese do artigo.

**Alternativa sugerida (já no `.bib`):** `\cite{goodfellow2016}` (*Deep Learning*, MIT Press) — a explicação canônica da Softmax para classificação multiclasse aparece no capítulo 6. `\cite{feng2019}` (já usada nas funções de ativação vizinhas) é também apropriada e mantém consistência com as demais funções de ativação listadas no mesmo bloco.

---

## 11. `\cite{abdelnasser2019}` — definição/funcionamento dos portões da LSTM

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:398-402`

**Trecho:**
> *"Portão de entrada (input gate): Tem o objetivo de atualizar, a partir do fluxo de dados de entrada, o estado de memória da célula \cite{abdelnasser2019}. (...) Portão de esquecimento (forget gate): ... \cite{abdelnasser2019}. Portão de saída (output gate): ... \cite{abdelnasser2019}."*

**Problema:** Abdel-Nasser & Mahmoud (2019) — *Accurate photovoltaic power forecasting models using deep LSTM-RNN* — é uma **aplicação** da LSTM a previsão de potência fotovoltaica. Os portões da LSTM são **conceitos originais** de Hochreiter & Schmidhuber (1997), reformulados (forget gate) por Gers et al. (1999/2000). Citar uma aplicação 22 anos posterior como fonte conceitual dos portões é uma escolha frágil.

**Alternativa sugerida (já no `.bib`):** `\cite{hochreiter1997}` (*Long Short-Term Memory*) — fonte primária da arquitetura LSTM e do conceito de "gates". `\cite{goodfellow2016}` (cap. 10) traz a apresentação didática equivalente. `\cite{graves2013}` é também aceitável para LSTM aplicado a sequências.

---

## 12. `\cite{ramakrishnan2018}` — definição geral de Redes Neurais Recorrentes (RNN)

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:381` e `451`

**Trecho (linha 381):**
> *"... Redes Neurais Recorrentes (Recurrent Neural Networks ou RNN) diferem substancialmente das tradicionais Redes Neurais Feedforward (FNN), pois possuem ciclos, permitindo que os dados de saída sejam alimentados de volta nas camadas anteriores. Isso torna o modelo capaz de capturar dependências temporais entre os dados \cite{ramakrishnan2018}."*

**Problema:** Ramakrishnan & Soni (2018) — *Network Traffic Prediction Using Recurrent Neural Networks* — é uma **aplicação** específica de RNN a previsão de tráfego de rede. Não é a fonte conceitual da definição de RNN; trata-se de um caso de uso.

**Alternativa sugerida (já no `.bib`):** `\cite{goodfellow2016}` (*Deep Learning*, cap. 10 sobre RNNs) ou `\cite{schmidhuber2015}` (*Deep learning in neural networks: An overview*) — ambas referências apresentam formalmente RNNs e suas propriedades. `\cite{haykin2001}` também cobre o tópico em livro-texto clássico.

---

## 13. `\cite{simard2003}` — definição de Convolutional Neural Networks (CNN)

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:469`

**Trecho:**
> *"... como demonstra o autor Jonghwan Mun, que utiliza um codificador CNN (Convolutional Neural Networks) \cite{simard2003}, um codificador RNN e um decodificador LSTM para um modelo que gera legendas de imagens \cite{mun2016}."*

**Problema:** Simard, Steinkraus & Platt (2003) é **"Best practices for convolutional neural networks applied to visual document analysis"** — um trabalho de **boas práticas em análise de documentos** com CNNs, e não a referência primária para definir CNN.

**Alternativa sugerida (já no `.bib`):** `\cite{lecun1998}` (*Gradient-based learning applied to document recognition*) — referência canônica das CNNs (LeNet). Alternativamente, `\cite{krizhevsky2017}` (AlexNet) ou `\cite{yamashita2018}` (overview de CNNs) — todas já presentes no `.bib`.

---

## 14. `\cite{fgv2023}` — aplicações principais do BIM

**Arquivo:** `dissertacao/Conteudo/01_Introducao.tex:7`

**Trecho:**
> *"O BIM permite criar modelos virtuais detalhados, facilitando a visualização e a detecção de interferências antes da construção física. As principais aplicações do BIM incluem análise de projetos, orçamento e planejamento, coordenação modular, gestão do ciclo de vida, visualização arquitetônica, entre outros \cite{fgv2023}."*

**Problema:** A referência é um **post de blog** institucional da FGV (*Digitalização na Construção: O Uso do BIM*) que toca o tema de forma superficial. Para uma afirmação técnica em dissertação de mestrado, uma fonte primária ou de livro-texto é mais apropriada — o post pode ser mantido como leitura complementar, mas não como base bibliográfica.

**Alternativa sugerida (já no `.bib`):** `\cite{eastman2011}` (*BIM Handbook*) — cobre exatamente todas as aplicações listadas (análise, orçamento, planejamento, coordenação, ciclo de vida, visualização). `\cite{coelho2018}` é uma segunda alternativa em português.

---

## 15. `\cite{penttila2016}` — definição operacional de BIM como conjunto de políticas/processos/ferramentas

**Arquivo:** `dissertacao/Conteudo/03_Fundamentacao_Teorica.tex:6`

**Trecho:**
> *"De acordo com \citeonline{penttila2016}, o BIM consiste em um conjunto estruturado de políticas, processos e ferramentas que formam uma metodologia para gerenciar os dados digitais e os projetos de construção ao longo do ciclo de vida do edifício."*

**Problema:** Dois pontos:

1. O artigo de Penttilä é de **2006** (Journal of Information Technology in Construction, vol.~11), não de 2016 como consta na entrada do `.bib`.
2. A definição na fonte original é mais enxuta: *"BIM is a methodology to manage the essential building design and project data in digital format throughout the building's life-cycle"*. A formulação no texto da dissertação parafraseia uma definição mais frequentemente atribuída a Succar/NBIMS, e não exatamente ao que Penttilä escreveu.

**Alternativa sugerida (já no `.bib`):** Para a definição "políticas, processos e ferramentas", `\cite{eastman2011}` é a referência clássica. Se desejar manter Penttilä, recomenda-se ajustar a paráfrase para refletir a definição original e **corrigir o ano para 2006** na entrada do `.bib`.

---

## Resumo

| # | Citação atual | Onde | Alternativa recomendada (no `.bib`) |
|---|---|---|---|
| 1 | `monteiro2011` | 03_Fund. linha 8 | `eastman2011` |
| 2 | `arroyo2000` | 03_Fund. linha 130 | `goodfellow2016` ou `schmidhuber2015` |
| 3 | `inan2023` | 01_Intro. linha 19 | `zhao2023` ou `naveed2024` |
| 4 | `du2024` | 01_Intro. linha 25 | `fuchs2024` |
| 5 | `vargas2023` | 01_Intro. linha 17 e 03_Fund. linha 47 | `dimyadi2013` ou `solihin2015` |
| 6 | `fuchs2024` (isolado) | 01_Intro. linha 13 | `rane2023` + `liu2022` |
| 7 | `devlin2019` | 03_Fund. linha 209 | `mikolov2013a`, `pennington2014`, `bojanowski2017` |
| 8 | `minsky1969` | 03_Fund. linha 239 | `rumelhart1986` ou `haykin2001` |
| 9 | `zhang2024` | 03_Fund. linhas 609 e 611 | `brown2020` |
| 10 | `sensoy2018` | 03_Fund. linha 306 | `goodfellow2016` ou `feng2019` |
| 11 | `abdelnasser2019` | 03_Fund. linhas 398-402 | `hochreiter1997` |
| 12 | `ramakrishnan2018` | 03_Fund. linhas 381 e 451 | `goodfellow2016` ou `schmidhuber2015` |
| 13 | `simard2003` | 03_Fund. linha 469 | `lecun1998` ou `krizhevsky2017` |
| 14 | `fgv2023` | 01_Intro. linha 7 | `eastman2011` |
| 15 | `penttila2016` | 03_Fund. linha 6 | `eastman2011` (e corrigir ano para 2006 no `.bib`) |

## Observações finais

- Não foram analisadas individualmente as citações cuja correspondência tema/título é direta (ex.: `eastman2011` para BIM, `hochreiter1997` para LSTM, `vaswani2017` para Transformer, `hjelseth2011` para RASE, `kusner2015` para WMD, `reimers2019` para SBERT, `souza2020` para BERTimbau, `abnt9050` para NBR 9050, `iso19650` para ISO 19650 etc.) — todas conferem com o trecho em que são usadas.
- Algumas entradas do `.bib` apresentam **inconsistências cadastrais** (não relacionadas ao mérito da citação) que vale revisar à parte: ano incorreto em `penttila2016` (correto: 2006); ano "2023" em `vargas2023` quando o artigo original é de 2017 (*Ambiente Construído*); título estranho/aparente erro de transcrição em `tafner1995`; entrada `hoch` (linha 410 do `.bib`) sem `title`/`author` propriamente preenchidos, usada como fonte da Figura 3.1.1.
- Este documento **não modifica** os arquivos `.tex` nem `.bib` — apenas reporta os achados, conforme solicitado.
