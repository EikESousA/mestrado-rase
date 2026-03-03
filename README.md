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

O objetivo principal do projeto é a leitura e interpretação automatizada de normas de engenharia, convertendo um código RASE para o formato JSON. Para isso, utiliza-se o modelo LLaMA 3, explorando técnicas avançadas de Engenharia de Prompt, Fine-Tuning e Recuperação Aumentada por Geração (RAG). Esse processo visa aprimorar a compreensão e estruturação dos dados extraídos das normas, proporcionando maior precisão e eficiência na conversão para um formato estruturado e de fácil manipulação.

### Sistema Operacional

Deve funcionar conforme pretendido no **Windows**, **Linux** ou **macOS**.

### Interpretador Python

Atualmente requer Python **3.11.9**.

## Estrutura rapida

- `main.py`: menu principal para gerar e validar dados.
- `generates/menu_generate.py`: menu de selecao de N e modelos.
- `validates/menu_validate.py`: menu de selecao de validacoes.
- `dataset.json`: entrada de textos.
- `regression/`: conjunto fixo de regressao (`cases.json`, `dataset_regression.json`, `run_regression.py`).
- `predicts/`: saida gerada.
- `metrics/`: saida das validacoes.

## Requisitos

- Python 3.11+.
- Ollama instalado e em execucao (`ollama serve`).
- Modelos serao baixados automaticamente pelo menu (quando necessario).
- O alias `llama3.1` do projeto usa `llama3.1:8b` por padrao para evitar que `:latest`
  resolva para variantes 70B pesadas demais para maquinas com 16 GB de VRAM. Para
  sobrescrever isso, defina `RASE_OLLAMA_MODEL_LLAMA3_1`.
- O alias `llama3.3` do projeto usa `llama3.3:70b-instruct-q2_K` por padrao, que e a
  variante oficial mais leve publicada no Ollama para esse modelo. Para sobrescrever isso,
  defina `RASE_OLLAMA_MODEL_LLAMA3_3`.
- O alias `llama4` do projeto usa `llama4:scout` por padrao. Em 3 de marco de 2026,
  essa e a menor variante oficial publicada na biblioteca do Ollama para Llama 4
  (67 GB na pagina de tags). Para sobrescrever isso, defina
  `RASE_OLLAMA_MODEL_LLAMA4`.
- Se um modelo especifico falhar no backend CUDA do Ollama, voce pode apontar os
  scripts para outra instancia definindo `RASE_OLLAMA_HOST`.

## Instalacao

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
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

Modo Teste no menu:

- Em `Gerar dados`, marque `t - teste` para gerar somente os 5 primeiros itens e salvar com sufixo `_test`.
- Em `Validar dados`, marque `t - teste` para validar usando os arquivos `*_test` e salvar metricas com sufixo `_test`.

## Funcionalidades (N1/N2/N3)

### Geracao N1

`generates/generate_n1.py` transforma os textos de `dataset.json` em sentencas N1 usando o prompt `prompts/n1.txt`. Cada entrada gera:

- `texts_n1`: lista com `text_n1` e `operators_n2` vazio (estrutura base para N2).
- Metadados: `counts` e `time`.

Como a geracao N1 e feita:

1. Le o `dataset.json` (ou `--input`).
2. Monta cadeia `prompt -> OllamaLLM`.
3. Executa ate 3 tentativas por texto (com timeout e log).
4. Limpa a saida e separa em sentencas via `utils/n1/process_text.py`.
5. Salva incrementalmente no JSON de saida para evitar perda em execucoes longas.

Opcoes de inferencia:

- `--temperature`, `--top-p`, `--top-k`, `--repeat-penalty`, `--seed`, `--num-ctx`, `--num-predict`.

Comando:

```bash
python generates/generate_n1.py --model mistral
```

Se quiser trocar o modelo real por tras de um alias sem editar codigo:

```bash
RASE_OLLAMA_MODEL_LLAMA3_1=llama3.1:8b python generates/generate_n1.py --model llama3.1
```

Para sobrescrever manualmente o alias `llama4` no projeto:

```bash
RASE_OLLAMA_MODEL_LLAMA4=<repo-ou-tag-do-ollama> python generates/generate_n1.py --model llama4
```

Workaround para `dolphin` quando o Ollama cair com `SIGSEGV` no backend CUDA:

1. Em um terminal, suba uma instancia local CPU-only:

```bash
./scripts/run_ollama_cpu_fallback.sh
```

2. Em outro terminal, aponte os scripts para essa instancia:

```bash
RASE_OLLAMA_HOST=http://127.0.0.1:11435 .venv/bin/python generates/generate_n1.py --model dolphin
```

O script de fallback reutiliza os modelos ja instalados em `/usr/share/ollama/.ollama/models`
e desativa CUDA/Flash Attention apenas para essa instancia local.

No menu, o modelo `qwen` usa automaticamente esse fallback CPU-only quando nenhum
`RASE_OLLAMA_HOST` estiver definido, porque a combinacao atual de Ollama + backend GPU
esta derrubando o runner desse GGUF. Para desativar esse comportamento automatico,
defina `RASE_DISABLE_AUTO_CPU_FALLBACK=1`.

### Geracao N2

`generates/generate_n2.py` preenche os operadores N2 a partir das sentencas N1. Ele espera um arquivo com `texts_n1` (normalmente a saida do N1) e usa o prompt `prompts/n2.txt`.

Como a geracao N2 e feita:

1. Para cada `text_n1`, chama o modelo com contexto (`text` + `text_n1`).
2. A saida e parseada por `utils/n2/process_text.py`:
   - aceita JSON (preferencial),
   - aceita formato legado em linhas (`aplicabilidade: ...`).
3. A resposta passa por validacao minima (requisito obrigatorio, campos sem lixo estrutural).
4. Se falhar, repete ate 3 tentativas.
5. Converte para `operators_n2` com os 4 campos padrao (`aplicability`, `selection`, `exception`, `requeriments`).
6. Logs incluem rastreio estavel por `text_index` e `sentence_index`.

Comando:

```bash
python generates/generate_n2.py --model mistral
```

Opcoes uteis (N2/N3):

- `--strict-json`: rejeita respostas fora de JSON valido e tenta novamente.
- `--no-json-format`: desativa forcar `format=json` no Ollama.
- `--temperature`, `--top-p`, `--top-k`, `--repeat-penalty`, `--seed`, `--num-ctx`, `--num-predict`.

### Geracao N3

`generates/generate_n3.py` preenche `properties_n3` para cada operador N2. Usa prompts especificos por operador em `prompts/n3_*.txt`.

Como a geracao N3 e feita:

1. Percorre cada operador N2 nao vazio.
2. Tenta fallback deterministico (`utils/n3/fallback_properties.py`) para casos frequentes.
3. Se nao houver fallback aplicavel, chama o modelo (ate 3 tentativas).
4. Parseia JSON com `utils/n3/parse_properties.py`.
5. Valida e normaliza semantica com `utils/n3/validate_properties.py`:
   - normaliza `type`,
   - valida consistencia (`comparation` exige `property` e `target`),
   - padroniza alvos booleanos (`VERDADEIRO`/`FALSO`).
6. Em falha, mantem estrutura vazia do operador.
7. Logs incluem rastreio estavel por `text_index`, `sentence_index` e `operator`.

Comando:

```bash
python generates/generate_n3.py --model mistral
```

### Geracao N1+N2+N3

`generates/generate_n1n2n3.py` aplica o N3 sobre um arquivo N1+N2 (ex: `predicts/generate_n1n2_<modelo>.json`) e grava em `predicts/generate_n1n2n3_<modelo>.json`.

Comando:

```bash
python generates/generate_n1n2n3.py --model mistral
```

### Validacao N1

`validates/validate_n1.py` compara as sentencas N1 geradas com o `dataset.json` e grava metricas em `metrics/validate_n1.json`. Sao usadas:

- Exact Match (normalizado)
- FuzzyWuzzy (similaridade parcial)
- TF-IDF
- SBERT (pt)
- BERTimbau (STS juridico pt-br)
- SentenceTransformer multilingual
- WMD (FastText e NILC, quando disponiveis)

Como a validacao N1 e feita:

1. Alinha sentencas reais e geradas por similaridade (nao por indice fixo).
2. Mantem sentencas sem par correspondente para penalizar excesso/falta de segmentacao.
3. Calcula metricas por par e medias por modelo.

### Validacao N2/N3

`validates/validate_n2.py` valida os operadores N2 (campos `text_n2`). `validates/validate_n3.py` valida as propriedades N3.

Como a validacao N2/N3 e feita:

1. Reaproveita alinhamento de sentencas N1 por similaridade.
2. Com sentencas alinhadas, compara operador a operador (`aplicability`, `selection`, `exception`, `requeriments`).
3. N3 transforma `properties_n3` em string canonica (`type|object|property|...`) antes de medir similaridade.
4. Calcula metricas por par e medias por modelo.
5. Calcula tambem `operator_presence_report` por operador (N2/N3) com:
   - `tp`, `fp`, `fn`, `tn`
   - `precision`, `recall`, `f1`
   - `macro_avg` e `micro_avg`

Comandos:

```bash
python validates/validate_n2.py
python validates/validate_n3.py
```

### Regressao fixa de prompts (12 textos)

Para reduzir regressao apos mudancas de prompt, o projeto inclui um subconjunto fixo com 12 textos em `regression/dataset_regression.json`.

Comando recomendado:

```bash
python regression/run_regression.py --models llama3.1
```

Esse runner:

1. Gera N1, N2 e N3 para o subconjunto fixo em `predicts/regression/`.
2. Gera aliases de pipeline (`generate_n1n2_*` e `generate_n1n2n3_*`) para validacoes combinadas.
3. Executa validacoes N1, N2, N3, N1N2 e N1N2N3 em `metrics/regression/`.

Opcoes uteis:

- `--models llama3.1,mistral` ou `--models all`
- `--refresh-dataset` (recria `dataset_regression.json` usando `cases.json` + `dataset.json`)
- `--skip-generate` / `--skip-validate`
- `--no-strict-json` (desativa `--strict-json` no N2/N3)

### Validacao N1+N2+N3

`validates/validate_n1n2n3.py` gera metricas combinadas para pipelines completos.

Como o consolidado e calculado:

1. Executa os blocos de validacao N1, N2 e N3.
2. Junta os itens por modelo.
3. Recalcula medias finais por metrica no conjunto agregado.

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
- Indices de alinhamento (`predicted_sentence_index`) e `alignment_score`.
- `text`: texto original completo.
- `text_n1`: sentenca N1 correspondente (no N2).
- `target`: texto de referencia do dataset.
- `predicted`: texto gerado pelo modelo.
- `exact_match`, `fuzzywuzzy`, `tfidf`, `sbert`, `multilingual`, `wmd_ft`, `wmd_nilc`: scores por par (0 a 1 quando aplicavel).

Nos arquivos de N2/N3 ha tambem:

- `operator_presence_report.<modelo>.by_operator.<operador>` com `tp`, `fp`, `fn`, `tn`, `precision`, `recall`, `f1`.
- `operator_presence_report.<modelo>.macro_avg` e `micro_avg`.

Pareamento de sentencas:

- O pareamento N1/N2/N3 usa alinhamento 1-para-1 por similaridade de sentenca, nao apenas indice fixo.
- Sentencas extras geradas e sentencas reais sem correspondente sao mantidas como pares (com um lado vazio), para penalizar o score final.

Interpretacao dos scores:

- `fuzzywuzzy`: similaridade parcial por caracteres.
- `exact_match`: igualdade exata apos normalizacao basica (lowercase e espacos).
- `tfidf`: similaridade cosseno em TF-IDF.
- `sbert`: similaridade semantica com SBERT pt.
- `multilingual`: similaridade semantica multilingue.
- `wmd_ft`: similaridade derivada do Word Mover's Distance com FastText.
- `wmd_nilc`: similaridade derivada do Word Mover's Distance com NILC (quando disponivel).

Os valores em `averages` sao medias simples de cada metrica, ignorando valores ausentes. Quanto mais proximo de 1, maior a similaridade entre `target` e `predicted` em todas as metricas, incluindo WMD (que ja e normalizado).

Observacao importante:

- `exact_match` e util para medir aderencia estrita de forma conservadora.
- metricas semanticas (`sbert`, `bertimbau`, `multilingual`) capturam equivalencia de sentido mesmo com reescrita lexical.

## Ajuda

Se você tiver dúvidas, relatórios de bugs ou solicitações de recursos, não hesite em nos mandar mensagem para o email **eike.sousa@hotmail.com**.

Lembre-se de seguir nosso **[Código de Conduta](https://github.com/EikESousA/IAnvisa/blob/main/CODE_OF_CONDUCT.md)**.

## Licença

Licenciado pelo CC0-1.0 license. Consulte o arquivo **[LICENSE](https://github.com/EikESousA/IAnvisa/blob/main/LICENSE)** para obter detalhes.
