# Repository Guidelines

## Project Structure & Module Organization
- `main.py` provides the interactive menu for generation and validation.
- `generates/` contains generation scripts (`generate_n1.py`, `generate_n2.py`, `generate_n3.py`, `generate_n1n2.py`, `generate_n1n2n3.py`) and the menu.
- `validates/` contains validation scripts (`validate_n1.py`, `validate_n2.py`, `validate_n3.py`, `validate_n1n2.py`, `validate_n1n2n3.py`) and the menu.
- `utils/` houses shared helpers (generation, validation, logging, screen UI).
- `utils/n3/` includes parser, semantic validator and deterministic fallback:
  - `parse_properties.py`
  - `validate_properties.py`
  - `fallback_properties.py`
- `utils/validates/` includes pair builders and metric helpers:
  - `build_pairs.py`
  - `match_sentences.py`
  - `compute_exact_match_scores.py`
  - `operator_presence_report.py`
- `prompts/` stores prompt templates for N1/N2/N3.
- `regression/` stores fixed regression artifacts:
  - `cases.json` (indices fixos)
  - `dataset_regression.json` (subset fixo com 12 textos)
  - `run_regression.py` (execucao completa de geracao + validacao)
- `dataset.json` is the input text dataset.
- `predicts/` stores generated outputs.
- `metrics/` stores validation outputs.
- `docs/` stores images and badges.
- `test.py` runs a small N1->N2->N3 pipeline on the first dataset item and writes `predicts/generate_test.py`.

## Build, Test, and Development Commands
Install dependencies (Python 3.11.9 recommended):
```bash
pip install -r requirements.txt
```
Train dependencies live in `src/train/requirements.txt`:
```bash
pip install -r src/train/requirements.txt
```
Run generation scripts:
```bash
python generates/generate_n1.py --model llama3.1
python generates/generate_n2.py --model llama3.1 --strict-json
python generates/generate_n3.py --model llama3.1 --strict-json
python generates/generate_n1n2n3.py --model llama3.1 --strict-json
```
Generation tuning options:
```bash
--temperature --top-p --top-k --repeat-penalty --seed --num-ctx --num-predict
```
JSON control options (N2/N3):
```bash
--strict-json
--no-json-format
```
Run validation scripts:
```bash
python validates/validate_n1.py
python validates/validate_n2.py
python validates/validate_n3.py
python validates/validate_n1n2n3.py
```
Run a small pipeline sample:
```bash
python test.py
```
Menu quick-test mode:
- In `Gerar dados`, toggle `t` to generate only the first 5 items and write `*_test.json`.
- In `Validar dados`, toggle `t` to read `*_test.json` files and write `metrics/*_test.json`.
Run fixed regression suite (recommended after prompt changes):
```bash
python regression/run_regression.py --models llama3.1
```

## Coding Style & Naming Conventions
- Python files use 4-space indentation; keep code readable and minimal.
- Follow existing naming patterns: `snake_case` for functions/variables, concise script names (e.g., `generate_n1.py`).
- No formatter or linter is configured; avoid large style-only diffs.

## Testing Guidelines
- No automated test runner is set up.
- Validate changes by running relevant generators/validators and checking JSON outputs in `predicts/` and `metrics/`.
- Useful sanity check:
```bash
python -m compileall generates validates utils
```

## Commit & Pull Request Guidelines
- Commit messages in history are short, title-style summaries (e.g., `Generate N1`, `Readme`, `Models`). Keep them concise and task-focused.
- PRs should describe what changed, how to reproduce (commands), and link any relevant data/artifacts. Include screenshots only when updating docs/plots.

## Configuration Notes
- External dependencies include `ollama` and CUDA Toolkit 11.8 for GPU workflows.
- Use a virtual environment (`venv` or `conda`) to isolate Python dependencies.

## N1, N2, N3 (Fluxo e Conversao)
- **N1 (`generates/generate_n1.py`)**
  - Input: `dataset.json`
  - Prompt: `prompts/n1.txt`
  - Output: `texts_n1[].text_n1`
  - Also initializes `operators_n2` vazio para a proxima etapa.
  - Prompt foi ajustado para reduzir super-segmentacao.

- **N2 (`generates/generate_n2.py`)**
  - Input: arquivo com `texts_n1` (tipicamente saida do N1).
  - Prompt: `prompts/n2.txt`
  - Extrai 4 operadores:
    - `aplicability`
    - `selection`
    - `exception`
    - `requeriments`
  - Cada operador:
    - `text_n2`
    - `properties_n3` inicial vazio (`type`, `object`, `property`, `comparation`, `target`, `unit`)
  - Retry usa validacao de saida (nao para na primeira resposta invalida).
  - Parser aceita JSON e formato legado em linhas.
  - Logs incluem IDs estaveis (`text_index`, `sentence_index`).

- **N3 (`generates/generate_n3.py`)**
  - Input: arquivo com `operators_n2` (tipicamente saida do N2).
  - Prompts especificos por operador: `prompts/n3_*.txt`.
  - Converte `text_n2` em `properties_n3`.
  - Usa parse estruturado + validacao semantica pos-parse.
  - Pode usar fallback deterministico por regex para casos recorrentes.
  - `format=json` fica ativo por padrao (desativavel com `--no-json-format`).
  - Logs incluem IDs estaveis (`text_index`, `sentence_index`, `operator`).

- Conversao final esperada (alinhada ao `dataset.json`):
  - `datas[] -> texts_n1[] -> operators_n2[operador] -> properties_n3`
  - Campos finais de `properties_n3`: `type`, `object`, `property`, `comparation`, `target`, `unit`

## Validacao e Metricas
- Validadores:
  - `validates/validate_n1.py`
  - `validates/validate_n2.py`
  - `validates/validate_n3.py`
  - `validates/validate_n1n2.py`
  - `validates/validate_n1n2n3.py`
- Metricas atuais:
  - `exact_match`
  - `fuzzywuzzy`
  - `tfidf`
  - `sbert`
  - `bertimbau`
  - `multilingual`
  - `wmd_ft`
  - `wmd_nilc`
- Pareamento de sentencas:
  - N1/N2/N3 usam alinhamento 1-para-1 por similaridade (nao apenas indice fixo).
  - Sentencas extras/faltantes entram na avaliacao como pares com lado vazio para penalizar.
  - Campos de rastreio incluem `predicted_sentence_index` e `alignment_score`.
- Relatorio por operador (N2/N3):
  - `operator_presence_report` com `tp`, `fp`, `fn`, `tn`, `precision`, `recall`, `f1`.
  - Agregacoes `macro_avg` e `micro_avg` por modelo.

## Melhorias Ja Implementadas
- Prompt N1 ajustado para reduzir fragmentacao excessiva.
- Prompt N2 migrado para saida JSON.
- `--strict-json` para N2/N3.
- Exposicao de parametros de inferencia por CLI (`temperature`, `top_p`, `top_k`, `repeat_penalty`, `seed`, `num_ctx`, `num_predict`).
- Validacao semantica pos-N3.
- Fallback deterministico no N3 para padroes recorrentes.
- Alinhamento por similaridade na validacao (N1/N2/N3).
- Inclusao de `exact_match` nas metricas.
- Conjunto fixo de regressao com 12 textos (`regression/dataset_regression.json`) e runner dedicado.
- Relatorio explicito de precision/recall/f1 por operador em N2/N3 (`operator_presence_report`).
- Rastreabilidade com IDs estaveis em logs de geracao (`text_index`, `sentence_index`, `operator`).
