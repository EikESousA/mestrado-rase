<p align="center">
  <img src="docs/images/ufs.png" alt="Logo da UFS" aling="center" width="10%"/>
  <img src="docs/images/procc.png" alt="Logo da PROCC" aling="center" width="17%"/>
</p>

<p align="center">
  <img src="docs/tags/release.svg" alt="Icone da Versão" />
  <img src="docs/tags/license.svg" alt="Icone de Licença" />
  <img src="docs/tags/contributors.svg" alt="Icone da Cobertura" />
</p>

<p align="center">
  <img src="docs/tags/plataform.svg" alt="Icone da Versão" />
  <img src="docs/tags/build.svg" alt="Icone da Construção" />  
  <img src="docs/tags/coverage.svg" alt="Icone da Cobertura" />
</p>

# Mestrado RASE

Este código foi desenvolvido como parte do Mestrado do aluno Eike Natan Sousa Brito, no Programa de Pós-Graduação em Ciência da Computação (PROCC) da Fundação Universidade Federal de Sergipe (UFS), durante o período de 2024-2025.

O objetivo principal do projeto é a leitura e interpretação automatizada de normas de engenharia, convertendo um código RASE para o formato JSON. O pipeline atual utiliza **Engenharia de Prompt** sobre seis LLMs locais servidos pelo Ollama (Llama 3.3, Bode-Alpaca PT-BR, Mistral PT, Dolphin PT, Gemma Gaia PT-BR e Qwen2.5 PT), aplicando-os em três níveis sequenciais: **N1** (segmentação em sentenças), **N2** (identificação dos operadores RASE — *Requirements*, *Applicability*, *Selection*, *Exception*) e **N3** (extração estruturada das propriedades). A validação compara as saídas com o `dataset.json` de referência usando 7 métricas de similaridade e 4 métricas de classificação.

### Sistema Operacional

Deve funcionar conforme pretendido no **Windows**, **Linux** ou **macOS**.

### Interpretador Python

Recomendado Python **3.11.9**. Funciona em Python **3.12** (testado).

## Estrutura rapida

- `main.py`: menu principal para gerar e validar dados.
- `config/models.py`: lista central dos modelos Ollama (nomes + IDs).
- `generates/menu_generate.py`: menu de selecao de N e modelos.
- `validates/menu_validate.py`: menu de selecao de validacoes.
- `prompts/`: templates `n1.txt`, `n2.txt`, `n3_*.txt` (per-operador) e `n3_combined.txt` (multi-operador).
- `dataset.json`: entrada de textos.
- `predicts/`: saida gerada.
- `metrics/`: saida das validacoes.
- `utils/validates/run_validation.py`: orquestrador unico das validacoes (compartilhado pelos 5 scripts).

## Requisitos

- Python 3.11+ (3.12 funciona).
- Ollama instalado e em execucao (`ollama serve`).
- Modelos serao baixados automaticamente pelo menu (quando necessario).
- A metrica WMD usa `pot` (Python Optimal Transport), ja listado em `requirements.txt`.
- Os pesos NILC FastText/Word2Vec (Portugues) sao baixados sob demanda do Hugging Face em `wmd_ft`/`wmd_nilc`.

## Instalacao

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Alternativa rapida com [uv](https://docs.astral.sh/uv/) (nao requer `python3-venv`):

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
```

## Como iniciar

1. Garanta que o Ollama esteja rodando:

```bash
ollama serve
```

2. Inicie o menu principal:

```bash
python3 main.py
```

No menu, escolha "Gerar dados" e selecione o N (n1/n2/n3/n1n2/n1n2n3) e o modelo. O sistema usara `dataset.json` como entrada.

## Funcionalidades (N1/N2/N3)

### Geracao N1

`generates/generate_n1.py` transforma os textos de `dataset.json` em sentencas N1 usando o prompt `prompts/n1.txt`. Cada entrada gera:

- `texts_n1`: lista com `text_n1` e `operators_n2` vazio (estrutura base para N2).
- Metadados: `counts` e `time`.

Comando:

```bash
python generates/generate_n1.py --model mistral
```

### Geracao N2

`generates/generate_n2.py` preenche os operadores N2 a partir das sentencas N1. Ele espera um arquivo com `texts_n1` (normalmente a saida do N1) e usa o prompt `prompts/n2.txt`.

Comando:

```bash
python generates/generate_n2.py --model mistral
```

### Geracao N3

`generates/generate_n3.py` preenche `properties_n3` para cada operador N2. Por padrao usa um **prompt unico multi-operador** (`prompts/n3_combined.txt`) que retorna o JSON dos 4 operadores em uma so chamada do LLM — ~4x mais rapido que o modo legacy.

Comando:

```bash
python generates/generate_n3.py --model mistral
```

Para reverter ao modo legacy (4 chamadas por sentenca, uma por operador, com prompts em `prompts/n3_*.txt`):

```bash
N3_LEGACY=1 python generates/generate_n3.py --model mistral
```

### Geracao N1+N2+N3

`generates/generate_n1n2n3.py` aplica o N3 sobre um arquivo N1+N2 (ex: `predicts/generate_n1n2_<modelo>.json`) e grava em `predicts/generate_n1n2n3_<modelo>.json`.

Comando:

```bash
python generates/generate_n1n2n3.py --model mistral
```

### Validacao N1

`validates/validate_n1.py` compara as sentencas N1 geradas com o `dataset.json` e grava metricas em `metrics/validate_n1.json`. Sao usadas 7 metricas de similaridade e 4 de classificacao:

Similaridade:

- FuzzyWuzzy (similaridade parcial por caracteres)
- TF-IDF (cosseno)
- SBERT pt (`tgsc/sentence-transformer-ult5-pt-small`)
- BERTimbau Legal (`rufimelo/Legal-BERTimbau-sts-large-ma-v3`)
- Multilingual (`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`)
- WMD com NILC FastText PT (`nilc-nlp/fasttext-cbow-300d`)
- WMD com NILC Word2Vec PT (`nilc-nlp/word2vec-cbow-300d`)

Classificacao (derivada do par alinhado por indice, threshold de similaridade 0,7 sobre Multilingual):

- Accuracy, Precision, Recall, F1
- Em N2 reportada tambem por operador (R, A, S, E) e macro-media.
- Em N3 reportada por campo (`object`, `property`, `comparation`, `target`, `unit`) e macro-media (correspondencia exata apos normalizacao).

### Validacao N2/N3

`validates/validate_n2.py` valida os operadores N2 (campos `text_n2`). `validates/validate_n3.py` valida as propriedades N3.

Comandos:

```bash
python validates/validate_n2.py
python validates/validate_n3.py
```

### Validacao N1+N2+N3

`validates/validate_n1n2n3.py` gera metricas combinadas para pipelines completos.

Comandos:

```bash
python validates/validate_n1n2n3.py
```

### Teste rapido (pipeline N1 -> N2 -> N3)

`test.py` executa uma amostra com o primeiro item do `dataset.json`, gerando N1, N2 e N3 e validando cada etapa. O resultado final fica em `predicts/generate_test.py`.

```bash
python test.py
```

## Saidas

Os arquivos gerados ficam em `predicts/` no formato:

- `predicts/generate_<n>_<modelo>.json`

Exemplos:

- `predicts/generate_n1_mistral.json`
- `predicts/generate_n1_llama.json`
- `predicts/generate_n3_mistral.json`
- `predicts/generate_n1n2_mistral.json`
- `predicts/generate_n1n2n3_mistral.json`

Cada arquivo contem um JSON com `counts`, `time` e `datas`.

- `counts`: total de textos processados.
- `time`: tempo total (segundos) da execucao completa.
- `datas`: lista de itens com o texto original e as estruturas geradas.

Para N1, cada item em `datas` contem:

- `text`: texto original do dataset.
- `texts_n1`: lista de sentencas N1, cada uma com `text_n1` e `operators_n2` vazio (estrutura pronta para N2).

Para N2, cada item em `datas` contem:

- `text`: texto original do dataset.
- `texts_n1`: lista de sentencas N1 com `operators_n2` preenchido. Cada operador possui `text_n2` (frase/trecho gerado) e `properties_n3` (estrutura de N3).

Para N3 (e combinacoes), cada item em `datas` contem o mesmo formato de N2, com `properties_n3` preenchido.

## Validacoes

Os arquivos de validacao ficam em `metrics/` (ex: `metrics/validate_n1.json`, `metrics/validate_n2.json`, `metrics/validate_n3.json`).

Cada arquivo de validacao possui:

- `models`: resultados detalhados por modelo, contendo `counts` e `items`.
- `averages`: medias agregadas por modelo para cada metrica.

Em `models.<modelo>.items`, cada item inclui:

- Indices (`text_index`, `sentence_index`) e, no N2, o `operator`.
- `text`: texto original completo.
- `text_n1`: sentenca N1 correspondente (no N2).
- `target`: texto de referencia do dataset.
- `predicted`: texto gerado pelo modelo.
- `fuzzywuzzy`, `tfidf`, `sbert`, `bertimbau`, `multilingual`, `wmd_ft`, `wmd_nilc`: scores por par (0 a 1 quando aplicavel).

Cada entrada de `models.<modelo>` tambem inclui `classification` com:

- `overall`: TP/FP/FN/TN + accuracy/precision/recall/f1 (agregado).
- `by_operator` (N2): metricas por operador R/A/S/E.
- `by_field` (N3): metricas por campo do JSON.
- `macro`: media das submetricas.

Interpretacao dos scores:

- `fuzzywuzzy`: similaridade parcial por caracteres.
- `tfidf`: similaridade cosseno em TF-IDF.
- `sbert`: similaridade semantica com SBERT pt (`ult5-pt-small`).
- `bertimbau`: similaridade semantica com BERTimbau Legal.
- `multilingual`: similaridade semantica multilingue.
- `wmd_ft`: similaridade derivada do Word Mover's Distance com NILC FastText PT.
- `wmd_nilc`: similaridade derivada do Word Mover's Distance com NILC Word2Vec PT.

Os valores em `averages` sao medias simples de cada metrica, ignorando valores ausentes; o campo `classification_macro` traz a macro-media de accuracy/precision/recall/f1. Quanto mais proximo de 1, maior a similaridade entre `target` e `predicted` em todas as metricas, incluindo WMD (que ja e normalizado para [0,1]).

## Variaveis de ambiente

Geracao (defaults ja otimizados — exportar so para opt-out):

- `GENERATE_DEBUG=0` — desliga logs em `logs/` (default ligado).
- `GEN_SEED=42` — seed deterministica do Ollama (default; setar `none` desliga).
- `GEN_RESUME=0` — desliga retomada por checkpoint (default ligado).
- `N3_LEGACY=1` — N3 usa 4 chamadas (uma por operador) em vez do prompt combinado.
- `GEN_TIMEOUT=600` — timeout em segundos por chamada LLM.
- `GEN_HEARTBEAT=30` — intervalo (segundos) entre mensagens de "ainda aguardando...".
- `USE_OLLAMA_DIRECT=1` — substitui `langchain_ollama` por cliente `ollama` direto.

Validacao (defaults ja otimizados — exportar so para opt-out):

- `VALIDATE_HUNGARIAN=0` — usa alinhamento por indice (default = Hungarian/similaridade).
- `VALIDATE_BERTSCORE=0` — desativa a metrica BERTScore (default ligado).
- `VALIDATE_ROUGE=0` — desativa a metrica ROUGE-L (default ligado).
- `METRICS_SPLIT_ITEMS=0` — items inline no JSON principal (default = split em jsonl).
- `SBERT_MODEL=<repo>` — sobrescreve o SBERT padrao
  (default `tgsc/sentence-transformer-ult5-pt-small`).

Logging:

- `LOG_FORMAT=json` — escreve logs em JSON Lines (`{"ts","iso","level","msg"}`).

Infra:

- `OLLAMA_HOST=http://...` — endereco do Ollama (default `http://localhost:11434`).
- `OLLAMA_HOSTS=http://a,http://b` — multiplos hosts; modelos distribuidos via ThreadPoolExecutor.
- `HF_TOKEN` (opcional) — token Hugging Face para evitar warnings de rate limit.

## Ferramentas auxiliares

- `tools/generate_tables.py` — gera tabelas LaTeX e CSV a partir de `metrics/`.
- `tools/run_seed_sweep.py` — roda multiplas seeds e calcula media/desvio.
- `tools/baseline_regex.py` — baseline nao-LLM (regex) para comparacao.
- `tools/quality_time.py` — calcula F1/segundo por modelo (qualidade vs custo).

## Docker

```bash
docker compose up --build
```

Sobe um container `ollama` e o app com volumes para os pesos. Veja `docker-compose.yml`.

## Ajuda

Se você tiver dúvidas, relatórios de bugs ou solicitações de recursos, não hesite em nos mandar mensagem para o email **eike.sousa@hotmail.com**.

Lembre-se de seguir nosso **[Código de Conduta](https://github.com/EikESousA/IAnvisa/blob/main/CODE_OF_CONDUCT.md)**.

## Licença

Licenciado pelo CC0-1.0 license. Consulte o arquivo **[LICENSE](https://github.com/EikESousA/IAnvisa/blob/main/LICENSE)** para obter detalhes.
