# Runbook — executar e coletar dados

Guia operacional para rodar geração + validação completas e coletar todos os artefatos do projeto. **Use sempre o menu interativo (`python main.py`) quando possível.** CLI direto aparece apenas onde não há opção de menu.

---

## 0. Pré-requisitos (setup único)

```bash
cd /home/eike/mestrado/mestrado-rase

# Se o .venv ja existe (caso desta maquina):
source .venv/bin/activate

# Confirma que tudo importa
python -c "from validates.validate_n1 import validate_n1; print('OK')"
```

Se for em outra máquina (sem `.venv`):

```bash
# Opcao A: uv (recomendado, ja instalado em ~/.local/bin)
~/.local/bin/uv venv .venv --python 3.12 --clear
~/.local/bin/uv pip install --python .venv/bin/python -r requirements.txt
source .venv/bin/activate

# Opcao B: venv tradicional (precisa sudo apt install python3-venv)
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

---

## 1. Subir Ollama

```bash
# Em outro terminal, deixe Ollama servindo
ollama serve
```

Os 6 modelos são instalados automaticamente pelo menu de geração (`ensure_model_installed` faz `ollama pull` sob demanda). Nada precisa ser baixado manualmente.

---

## 2. Geração (popular `predicts/`)

```bash
python main.py
```

No menu:

1. Pressione **`1`** (Gerar dados).
2. Marque os níveis com **`1`–`5`** (n1, n2, n3, n1n2, n1n2n3).
3. Marque os modelos com **`a`–`f`** (alpaca, dolphin, llama, mistral, gemma, qwen).
4. Pressione **Enter** para processar.

> **Defaults aplicados automaticamente:** seed 42, retomada de checkpoint e logs em `logs/`. Nada precisa ser exportado.

### Tempo estimado

| Modelo  | N1+N2+N3 (modo combinado) |
|---------|---------------------------|
| Qwen    | ~10 min                   |
| Mistral | ~30 min                   |
| Dolphin | ~30 min                   |
| Gemma   | ~30 min                   |
| Alpaca  | ~1 h                      |
| Llama   | ~3-5 h                    |

Total realista para tudo seriado: **24-30h** (Llama é o gargalo).

### Opt-out dos defaults (exportar antes de abrir o menu)

```bash
export GEN_SEED=none      # remove seed (resultados estocasticos)
export GEN_RESUME=0       # forca refazer do zero, ignora checkpoint
export GENERATE_DEBUG=0   # silencia logs
export N3_LEGACY=1        # N3 usa 4 chamadas por sentenca (modo antigo)
export USE_OLLAMA_DIRECT=1   # substitui langchain_ollama por cliente ollama
export OLLAMA_HOSTS=http://host-a:11434,http://host-b:11434  # multi-host paralelo
python main.py
```

---

## 3. Validação (popular `metrics/`)

```bash
python main.py
```

No menu:

1. Pressione **`2`** (Validar dados).
2. Marque com **`1`–`5`** quais experimentos validar.
3. Pressione **Enter** para processar.

### Defaults ja ligados

A validação ja roda por padrão com:

- **Alinhamento Hungarian** (similaridade SBERT em vez de índice) — mais correto.
- **Split de items** em `metrics/details/*.jsonl` — JSON principal so com averages.
- **BERTScore** e **ROUGE-L** ativos.
- **Logs detalhados** em `logs/`.

### Opt-out (exportar antes de abrir o menu)

```bash
export VALIDATE_HUNGARIAN=0           # volta ao alinhamento por indice
export METRICS_SPLIT_ITEMS=0          # items inline no JSON principal
export VALIDATE_BERTSCORE=0           # desliga BERTScore (mais rapido)
export VALIDATE_ROUGE=0               # desliga ROUGE-L
export SBERT_MODEL=neuralmind/bert-base-portuguese-cased  # trocar SBERT pequeno
python main.py
```

### Tempo estimado
~10-15 min por validador. Primeira execução baixa pesos NILC + BERTimbau (~2GB); execuções seguintes usam cache.

---

## 4. Tabelas LaTeX e CSV (popular `tables/`)

Sem opção de menu. CLI direto:

```bash
python tools/generate_tables.py --metrics-dir metrics --out-dir tables
```

Saída:

- `tables/results_n1_similarity.tex` — 6 modelos × 9 métricas de similaridade.
- `tables/results_n1_classification.tex` — 6 modelos × 4 métricas de classificação.
- `tables/results_n1.csv` — mesmo conteúdo em CSV.
- (idem para `n2`, `n3`, `n1n2`, `n1n2n3`)

---

## 5. Análise auxiliar (opcional)

Sem opção de menu. CLI direto:

```bash
# F1/segundo por modelo (qualidade vs custo)
python tools/quality_time.py \
  --metrics metrics/validate_n2.json \
  --predicts-dir predicts \
  --level n2 \
  --out tables/quality_time_n2.csv

# Baseline regex (referencia inferior)
python tools/baseline_regex.py --level n1 --output predicts/generate_n1_regex.json
python tools/baseline_regex.py --level n2 --output predicts/generate_n2_regex.json
python tools/baseline_regex.py --level n3 --output predicts/generate_n3_regex.json

# Sweep de seeds para medir variancia (3 seeds, modelo mistral)
python tools/run_seed_sweep.py \
  --level n2 --model mistral \
  --seeds 42 43 44 \
  --out-dir runs/seed_sweep
```

---

## 6. Onde estão TODOS os dados gerados

```
mestrado-rase/
├── predicts/
│   ├── generate_n1_<modelo>.json        # saidas N1 (1 por modelo)
│   ├── generate_n2_<modelo>.json        # saidas N2
│   ├── generate_n3_<modelo>.json        # saidas N3
│   ├── generate_n1n2_<modelo>.json      # pipeline N1+N2
│   └── generate_n1n2n3_<modelo>.json    # pipeline completo
├── metrics/
│   ├── validate_n1.json                 # 9 sim + 4 clf por modelo
│   ├── validate_n2.json                 # idem + by_operator (R/A/S/E)
│   ├── validate_n3.json                 # idem + by_field
│   ├── validate_n1n2.json               # combinado N1+N2
│   ├── validate_n1n2n3.json             # combinado N1+N2+N3
│   └── details/                         # split jsonl (default)
│       └── validate_<n>_<modelo>.jsonl  # 1 linha por par avaliado
├── tables/
│   ├── results_<n>_similarity.tex       # tabela LaTeX
│   ├── results_<n>_classification.tex
│   ├── results_<n>.csv                  # mesmo em CSV
│   └── quality_time_n2.csv              # F1/segundo
├── logs/
│   ├── generate_*.log                   # default ligado
│   └── generate_*.jsonl                 # se LOG_FORMAT=json
└── runs/seed_sweep/                     # se rodou seed_sweep
    ├── summary_n2_mistral.json          # media +/- stdev
    └── predict_n2_mistral_seed*.json
```

---

## 7. Inspecionar resultados rapidamente

Sem opção de menu. Snippet CLI:

```bash
python -c "
import json, glob
for f in sorted(glob.glob('metrics/validate_*.json')):
    print(f'\n=== {f} ===')
    d = json.load(open(f))
    avg = d.get('averages', {})
    for model, m in avg.items():
        line = [model]
        for k in ['fuzzywuzzy','tfidf','sbert','bertimbau','multilingual','wmd_ft','wmd_nilc','bertscore','rouge_l']:
            v = m.get(k)
            line.append(f'{k}={v:.3f}' if v is not None else f'{k}=-')
        clf = m.get('classification_macro', {})
        if clf:
            line.append(f'F1={clf.get(\"f1\",0):.3f}')
        print('  ' + '  '.join(line))
"
```

---

## 8. Caminho rápido (recomendado para a defesa)

Se o objetivo é apenas **atualizar os números para a tese** (sem regerar predicts):

1. Backup das métricas antigas:
   ```bash
   mv metrics metrics.old_$(date +%Y%m%d) && mkdir metrics
   ```
2. Abra o menu e rode todas as validações:
   ```bash
   python main.py
   # Pressione 2 (Validar) -> marque 1,2,3,4,5 -> Enter
   ```
3. Gere as tabelas:
   ```bash
   python tools/generate_tables.py
   python tools/quality_time.py
   ```

**Tempo**: ~1h. Já tem os números novos (`wmd_ft` em português, BERTimbau, BERTScore, ROUGE-L, classification, alinhamento Hungarian).

---

## 9. Docker (alternativa)

Se preferir isolar tudo em containers, sem opção de menu para subir:

```bash
docker compose up --build
```

`docker-compose.yml` sobe:

- `ollama`: serviço em `http://ollama:11434`.
- `app`: container com Python 3.11 + dependências + nltk pré-baixado.

Os volumes persistem pesos Ollama (`ollama-data`) e cache Hugging Face (`hf-cache`).

Dentro do container, use o menu normalmente:

```bash
docker compose exec app python main.py
```

---

## 10. Troubleshooting

### `wmdistance` retorna None
Falta `pot` (Python Optimal Transport). Resolver:
```bash
pip install pot
```

### `ImportError: No module named 'nltk'`
Reinstalar dependências:
```bash
pip install -r requirements.txt
```

### Ollama recusa conexão
Verificar se está rodando:
```bash
ollama list
# Se nao responder:
ollama serve &
```

### Geração trava em algum modelo
Aumentar timeout antes de abrir o menu:
```bash
export GEN_TIMEOUT=1200   # 20 min por chamada
export GEN_HEARTBEAT=15   # mensagem a cada 15s
python main.py
```

### `metrics/validate_n2.json` muito grande
Split já é o default. Items vão para `metrics/details/validate_n2_<modelo>.jsonl` automaticamente. Para reverter (items inline):
```bash
export METRICS_SPLIT_ITEMS=0
python main.py
```

### Quero retomar uma geração que caiu
É automático (`GEN_RESUME=1` é default). Basta reabrir o menu:
```bash
python main.py
# Pressione 1 (Gerar) e seleciona o mesmo N e modelo - retoma do checkpoint
```

### Aviso de rate limit do Hugging Face
Setar token (gratuito em huggingface.co/settings/tokens):
```bash
export HF_TOKEN=hf_xxxxx
python main.py
```
