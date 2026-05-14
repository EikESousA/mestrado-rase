# Otimizações para `mestrado-rase/`

Análise feita após varredura completa do código (`generates/`, `validates/`, `utils/`, `prompts/`, `main.py`, `test.py`, `requirements.txt`). As recomendações estão classificadas por **impacto** (🔴 alto, 🟡 médio, 🟢 baixo) e por **categoria** (Performance, Memória, Qualidade dos Resultados, Pesquisa, Código, Reprodutibilidade, Bugs).

> Marcadores de prioridade indicam o ganho prático esperado, não a dificuldade de implementação. Para cada item há um "Como aplicar" objetivo.

---

## 1. Performance — tempo de execução

### 🔴 1.1 Carregar modelos de embedding **uma vez** para todos os validadores

**Problema.** `validates/validate_n1.py`, `validate_n2.py`, `validate_n3.py`, `validate_n1n2.py` e `validate_n1n2n3.py` carregam SBERT, BERTimbau, Multilingual, FastText e NILC do zero a cada execução. Rodar os cinco validadores hoje significa carregar os mesmos modelos **5×**. Em uma máquina sem cache de pesos, isso adiciona dezenas de minutos.

**Como aplicar.**
- Criar um único *runner* `validates/validate_all.py` que carrega cada modelo uma vez e itera os cinco datasets de predição (N1, N2, N3, N1N2, N1N2N3) em sequência, gravando cinco arquivos de métricas.
- Alternativamente, mover o carregamento para `utils/validates/embedding_pool.py` com cache módulo-singleton (`functools.lru_cache(maxsize=1)`), e invocá-lo nos cinco scripts.

### 🔴 1.2 Vetorizar SBERT, BERTimbau e Multilingual

**Problema.** `compute_sbert_scores` e `compute_multilingual_scores` chamam `util.pytorch_cos_sim` dentro de um *for* — uma chamada por par (linhas 25–29 de cada). Para milhares de pares isso é dezenas de vezes mais lento que necessário.

**Como aplicar.** Calcular todos os embeddings em batch e fazer um único produto:
```python
T = model.encode(valid_targets, convert_to_tensor=True, normalize_embeddings=True, batch_size=64)
P = model.encode(valid_predictions, convert_to_tensor=True, normalize_embeddings=True, batch_size=64)
diag = (T * P).sum(dim=1)  # cosseno em lote, embeddings já normalizados
```
Ganho esperado: **3×–10×** dependendo da GPU.

### 🔴 1.3 Vetorizar TF-IDF

**Problema.** `compute_tfidf_scores` faz `cosine_similarity(matrix[i], matrix[i+n])[0][0]` dentro de um *for* (linhas 22–26). Isso é O(n) chamadas a `cosine_similarity` quando uma única chamada matricial bastaria.

**Como aplicar.**
```python
mat = vectorizer.fit_transform(valid_targets + valid_predictions)
T = mat[:len(valid_targets)]
P = mat[len(valid_targets):]
sims = (T.multiply(P)).sum(axis=1) / (np.linalg.norm(T.toarray(), axis=1) * np.linalg.norm(P.toarray(), axis=1))
# ou simplesmente:
sims = cosine_similarity(T, P).diagonal()
```
Ganho: **5×–20×**.

### 🔴 1.4 Eliminar `subprocess` por modelo no `run_generator`

**Problema.** `utils/generates/run_generator.py` usa `subprocess.run([sys.executable, script, "--model", model])` para cada modelo. Cada chamada paga o custo de inicialização do Python + import do langchain + import do `sentence-transformers` (não usado em geração, mas importado transitivamente). Esse custo é da ordem de **1–3 segundos por modelo**, multiplicado por níveis × 6 modelos = ~120s puramente em arranque.

**Como aplicar.** Importar a função `generate_n1` / `generate_n2` / `generate_n3` diretamente e chamá-la em loop no mesmo processo Python. Já existe a abertura para isso: `generate_n2` e `generate_n3` aceitam `input_path/output_path/model_id` como parâmetros — basta padronizar `generate_n1` da mesma forma e remover o `subprocess`.

### 🔴 1.5 Combinar as 4 chamadas de N3 em uma só

**Problema.** `generates/generate_n3.py` faz **4 chamadas separadas ao LLM por sentença N1** (uma por operador). Para Llama, que processa ~5min por chamada, isso cria as ~9450 segundos do experimento N1N2 do Llama.

**Como aplicar.**
- Unificar o prompt N3 em um único *system* prompt + *user* multi-operador, instruindo o modelo a produzir um único JSON com 4 chaves (`aplicabilidade`, `selecao`, `excecao`, `requisito`), cada uma com o sub-JSON. **Ganho: ~4×** no tempo de N3.
- Caso a qualidade caia, manter o prompt-por-operador apenas para o operador `requisito` (o mais sensível) e unificar os outros três.

### 🟡 1.6 Reduzir polling em `invoke_with_timeout`

**Problema.** `utils/generates/invoke_with_timeout.py` faz `time.sleep(0.2)` em loop ocupado para checar timeout/heartbeat. 5 calls/s × N segundos por chamada = milhares de wake-ups por execução longa.

**Como aplicar.** Usar `thread.join(timeout=heartbeat_interval)` no lugar do polling manual:
```python
while thread.is_alive():
    thread.join(timeout=heartbeat_interval)
    elapsed = time.time() - start
    if elapsed >= timeout:
        return None, True
    if log: log(f"Ainda aguardando... ({int(elapsed)}s)")
```

### 🟡 1.7 Não reescrever o JSON inteiro a cada iteração

**Problema.** `generate_n1.py:161-162`, `generate_n2.py:194-195` e `generate_n3.py:239-240` reescrevem o `output_path` inteiro a cada item processado. Para N3, são 79 textos × ~3 sentenças × 4 operadores = ~948 reescritas, e o arquivo cresce monotonicamente. Em SSD ainda é OK; em HDD ou ambientes com FS lento isso vira gargalo.

**Como aplicar.** Persistir um arquivo de checkpoint append-only (JSON Lines) e gerar o JSON consolidado apenas no final:
```python
with open(checkpoint_path, "a") as f:
    f.write(json.dumps(result_entry, ensure_ascii=False) + "\n")
# no final, agregar tudo num único JSON
```

### 🟡 1.8 Carregar prompts uma única vez

**Problema.** `PROMPT_PATH.read_text()` é chamado a cada início de execução, OK. Mas `ChatPromptTemplate.from_template(template)` recompila um *template* a cada iteração quando combinado com mudança de modelo — em scripts como `n1n2.py` que reusam `generate_n2`, o template já é fixo. Aqui o impacto é pequeno; deixe como está.

### 🟢 1.9 Substituir `langchain_ollama` por chamada direta

**Problema.** `langchain_ollama` adiciona uma camada de abstração que pesa ~200ms por chamada e traz dependências grandes (`langchain-core`).

**Como aplicar.**
```python
import ollama
client = ollama.Client(host="http://localhost:11434")
response = client.generate(model=model_id, prompt=prompt_filled, options={"temperature": 0.1, "top_p": 0.9, "repeat_penalty": 1.1})
text = response["response"]
```
Ganho marginal por chamada; ganho **estrutural** ao remover langchain das deps.

---

## 2. Memória

### 🔴 2.1 Não materializar todos os pares antes de validar

**Problema.** Os validadores constroem `model_data[model]["pairs"]` para todos os modelos antes de iniciar as métricas (`validate_n1.py:42-67`, idem N2/N3). Para N3, cada item carrega `target_properties` e `predicted_properties` (dicionários), `target` e `predicted` strings, e depois recebe 7 scores. Memória pico: 6 modelos × milhares de pares × ~1KB cada = MB de dicts vivos durante todo o processamento.

**Como aplicar.** Iterar **modelo por modelo**, calcular as 7 métricas para esse modelo, persistir, liberar. Memória pico cai para 1 modelo de cada vez.

### 🔴 2.2 Não armazenar `items` completos no JSON de métricas

**Problema.** `metrics["models"][model]["items"]` em `validate_n3.json` carrega: `text`, `text_n1`, `target_properties` (dict), `predicted_properties` (dict), `target` (string serializada), `predicted` (string serializada) + 7 scores. Para N3 com Llama, isso pode chegar a **megabytes** por arquivo.

**Como aplicar.**
- Manter apenas `averages` no arquivo `metrics/validate_<n>.json`.
- Persistir os *items* detalhados em `metrics/details/validate_<n>_<modelo>.jsonl` (uma linha por par).
- O capítulo de Resultados só precisa das médias; os detalhes ficam disponíveis para análise posterior sem inflar o repositório.

### 🟡 2.3 NILC carrega 1M+ palavras em RAM

**Problema.** `load_nilc_model` cria um `KeyedVectors` com todo o vocabulário NILC (centenas de milhares de palavras × 300 dim float32 = ~600MB).

**Como aplicar.**
- Filtrar o vocabulário para incluir apenas palavras presentes no dataset + nas predições antes de instanciar o `KeyedVectors`. Reduz uso de RAM em ~10× e acelera `wmdistance`.
- Salvar a versão filtrada em `models/nilc_filtered.kv` para reuso.

### 🟡 2.4 Liberar GPU entre métricas

**Problema.** `del sbert_model; gc.collect()` ajuda, mas não chama `torch.cuda.empty_cache()`. Em GPU compartilhada, fragmentação aumenta com o tempo.

**Como aplicar.**
```python
del sbert_model
gc.collect()
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

---

## 3. Qualidade dos resultados

### 🔴 3.1 WMD_FT está usando embeddings em **inglês**

**Problema crítico.** `validate_*.py:179` e `:198` carregam `api.load("fasttext-wiki-news-subwords-300")` — um modelo treinado **em inglês**. O dataset e as predições estão em **português**. As pontuações WMD_ft reportadas em `resultados.md` são, na prática, ruído estruturado: o modelo desconhece a maioria das palavras portuguesas e cai em fallback de sub-palavras.

**Como aplicar.**
- Trocar para FastText em português:
  ```python
  word_vectors_ft = api.load("fasttext-wiki-news-subwords-300")  # remover
  # alternativa 1: NILC FastText PT
  # alternativa 2: facebook/fasttext-pt-vectors via huggingface_hub
  ```
- Renomear a métrica para `wmd_pt_ft` e re-rodar a validação. **Os números do `resultados.md` provavelmente mudam significativamente.**

### 🔴 3.2 Validadores com BERTimbau + Accuracy / Precision / Recall / F1

> **Objetivo.** Alinhar a implementação dos validadores ao que está descrito no `plan.md`: manter as 7 métricas de similaridade já presentes (FuzzyWuzzy, TF-IDF, SBERT, **BERTimbau**, Multilingual, WMD_ft, WMD_nilc) e **adicionar** as 4 métricas de classificação (Accuracy, Precision, Recall, F1-score). Isso é pré-requisito para o capítulo de Resultados da dissertação.

#### 3.2.1 BERTimbau — confirmação do estado atual

**Estado atual no código (verificado em 2026-05-14):**

- `validates/validate_n1.py:98-114` — BERTimbau **já implementado** com `rufimelo/Legal-BERTimbau-sts-large-ma-v3`.
- `validates/validate_n2.py:140-156` — **já implementado**.
- `validates/validate_n3.py:159-175` — **já implementado**.
- `validates/validate_n1n2.py` e `validate_n1n2n3.py` — **verificar**, devem ter o mesmo bloco.

**Pendências:**

- Confirmar presença do bloco BERTimbau nos validadores combinados (`validate_n1n2.py` e `validate_n1n2n3.py`). Se ausente, copiar exatamente do `validate_n1.py`.
- Atualizar `README.md:120-125` para listar BERTimbau na seção de métricas de validação (atualmente lista apenas as outras 6).
- Recalcular as médias agregadas em `resultados.md` incluindo BERTimbau na tabela síntese — hoje a tabela tem 6 colunas, precisa de 7.

#### 3.2.2 Critérios de "acerto" para classificação

Para derivar Accuracy/Precision/Recall/F1, é necessário transformar pares (target, predicted) em rótulos binários (TP/FP/FN/TN). A definição varia por nível:

**N1 — Segmentação:**

- Cada `text_n1` real é considerado uma "instância positiva".
- Após alinhamento por similaridade entre `texts_n1` real e gerado (ver §3.3), definir:
  - **TP** = par alinhado com `multilingual >= 0,7` (limiar configurável).
  - **FN** = `text_n1` real sem par gerado correspondente (modelo gerou menos sentenças).
  - **FP** = `text_n1` gerado sem par real (modelo gerou sentenças a mais).
  - **TN** = não se aplica (não há rótulos negativos explícitos em segmentação).
- Métricas reportadas: **Precision**, **Recall**, **F1**. Accuracy fica como `TP / (TP + FP + FN)` (Jaccard, equivalente a F1 sem o fator 2).

**N2 — Identificação RASE:**

- Cada operador (R, A, S, E) por sentença N1 é uma instância potencial.
- **TP** = operador presente no real **e** no predito **e** com `multilingual >= 0,7` no `text_n2`.
- **FP** = operador presente no predito mas ausente no real (ou similaridade < 0,7).
- **FN** = operador presente no real mas ausente no predito (ou similaridade < 0,7).
- **TN** = operador ausente em ambos (real e predito retornam string vazia).
- Reportar Precision/Recall/F1 **por operador** (R, A, S, E) e **macro-média**.

**N3 — Extração estruturada:**

- Cada **campo do JSON** (`object`, `property`, `comparation`, `target`, `unit`) é uma instância.
- Comparação por **correspondência exata após normalização** (lowercase, remoção de acentos, remoção de pontuação trailing).
- **TP** = campo com valor não-vazio em ambos e iguais após normalização.
- **FP** = campo com valor no predito mas vazio (ou diferente) no real.
- **FN** = campo com valor no real mas vazio (ou diferente) no predito.
- **TN** = campo vazio em ambos.
- Reportar Precision/Recall/F1 **por campo** e **macro-média**.

#### 3.2.3 Implementação concreta — novo módulo

Criar `utils/validates/compute_classification_scores.py`:

```python
import unicodedata
from typing import Any, Dict, List, Tuple

THRESHOLD_DEFAULT: float = 0.7


def _normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    return text.lower().strip().rstrip(".,;:")


def _safe_div(num: float, den: float) -> float:
    return num / den if den > 0 else 0.0


def compute_confusion_from_similarity(
    similarities: List[float | None],
    targets: List[str],
    predictions: List[str],
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict[str, int]:
    """Para metricas baseadas em similaridade (N1/N2)."""
    tp = fp = fn = tn = 0
    for sim, t, p in zip(similarities, targets, predictions):
        t_has = bool(t and t.strip())
        p_has = bool(p and p.strip())
        if t_has and p_has:
            if sim is not None and sim >= threshold:
                tp += 1
            else:
                fp += 1
                fn += 1
        elif t_has and not p_has:
            fn += 1
        elif p_has and not t_has:
            fp += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def compute_confusion_from_exact(
    target_props: List[Dict[str, str]],
    predicted_props: List[Dict[str, str]],
    fields: Tuple[str, ...] = ("object", "property", "comparation", "target", "unit"),
) -> Dict[str, Dict[str, int]]:
    """Para N3 (correspondencia exata por campo)."""
    per_field: Dict[str, Dict[str, int]] = {
        f: {"tp": 0, "fp": 0, "fn": 0, "tn": 0} for f in fields
    }
    for t_props, p_props in zip(target_props, predicted_props):
        for field in fields:
            t_val = _normalize(t_props.get(field, "") if isinstance(t_props, dict) else "")
            p_val = _normalize(p_props.get(field, "") if isinstance(p_props, dict) else "")
            if t_val and p_val:
                if t_val == p_val:
                    per_field[field]["tp"] += 1
                else:
                    per_field[field]["fp"] += 1
                    per_field[field]["fn"] += 1
            elif t_val and not p_val:
                per_field[field]["fn"] += 1
            elif p_val and not t_val:
                per_field[field]["fp"] += 1
            else:
                per_field[field]["tn"] += 1
    return per_field


def metrics_from_confusion(conf: Dict[str, int]) -> Dict[str, float]:
    tp, fp, fn, tn = conf["tp"], conf["fp"], conf["fn"], conf["tn"]
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    accuracy = _safe_div(tp + tn, tp + tn + fp + fn)
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def macro_average(per_field_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    keys = ("accuracy", "precision", "recall", "f1")
    n = len(per_field_metrics)
    if n == 0:
        return {k: 0.0 for k in keys}
    return {
        k: sum(m[k] for m in per_field_metrics.values()) / n
        for k in keys
    }
```

#### 3.2.4 Integração nos validadores existentes

Após calcular as 7 métricas de similaridade em cada `validate_<n>.py`, adicionar **ao final do loop por modelo**:

```python
# Em validate_n1.py e validate_n2.py (apos popular data["scores"]):
from utils.validates.compute_classification_scores import (
    compute_confusion_from_similarity,
    metrics_from_confusion,
)

THRESHOLD = 0.7

for model, data in model_data.items():
    confusion = compute_confusion_from_similarity(
        similarities=data["scores"]["multilingual"],
        targets=data["targets"],
        predictions=data["predicted"],
        threshold=THRESHOLD,
    )
    classification = metrics_from_confusion(confusion)
    metrics["models"][model]["classification"] = classification
    metrics["averages"][model].update({
        "accuracy": classification["accuracy"],
        "precision": classification["precision"],
        "recall": classification["recall"],
        "f1": classification["f1"],
    })
```

Para **N2 com decomposição por operador** (recomendado pelo plan.md):

```python
operators = ("requeriments", "aplicability", "selection", "exception")
per_operator: Dict[str, Dict[str, float]] = {}
for op in operators:
    op_indices = [i for i, p in enumerate(data["pairs"]) if p["operator"] == op]
    op_sims = [data["scores"]["multilingual"][i] for i in op_indices]
    op_targets = [data["targets"][i] for i in op_indices]
    op_predicted = [data["predicted"][i] for i in op_indices]
    conf = compute_confusion_from_similarity(op_sims, op_targets, op_predicted, THRESHOLD)
    per_operator[op] = metrics_from_confusion(conf)
metrics["models"][model]["classification_by_operator"] = per_operator
metrics["averages"][model]["classification_macro"] = macro_average(per_operator)
```

Para **N3** (correspondência exata por campo):

```python
from utils.validates.compute_classification_scores import (
    compute_confusion_from_exact,
    metrics_from_confusion,
    macro_average,
)

target_props = [p["target_properties"] for p in data["pairs"]]
predicted_props = [p["predicted_properties"] for p in data["pairs"]]
per_field_conf = compute_confusion_from_exact(target_props, predicted_props)
per_field_metrics = {
    f: metrics_from_confusion(c) for f, c in per_field_conf.items()
}
metrics["models"][model]["classification_by_field"] = per_field_metrics
metrics["averages"][model]["classification_macro"] = macro_average(per_field_metrics)
```

#### 3.2.5 Estrutura final do JSON de métricas

Após implementação, `metrics/validate_n2.json` ficará assim (exemplo):

```json
{
  "models": {
    "llama": {
      "counts": 316,
      "items": [...],
      "classification_by_operator": {
        "requeriments": {"tp": 60, "fp": 8, "fn": 5, "tn": 5, "accuracy": 0.83, "precision": 0.88, "recall": 0.92, "f1": 0.90},
        "aplicability": {...},
        "selection": {...},
        "exception": {...}
      }
    }
  },
  "averages": {
    "llama": {
      "fuzzywuzzy": 0.761,
      "tfidf": 0.777,
      "sbert": 0.806,
      "bertimbau": 0.851,
      "multilingual": 0.869,
      "wmd_ft": 0.857,
      "wmd_nilc": 0.806,
      "classification_macro": {
        "accuracy": 0.81,
        "precision": 0.86,
        "recall": 0.88,
        "f1": 0.87
      }
    }
  }
}
```

#### 3.2.6 Métrica de similaridade usada como base para classificação

> **Decisão de projeto.** Recomenda-se usar **`multilingual`** (`paraphrase-multilingual-mpnet-base-v2`) como métrica base para os critérios TP/FP em N1 e N2, pelos seguintes motivos:
>
> 1. É a métrica com **maior média global** observada em `resultados.md` (EN1: 0,749; EN2: 0,668; EN1N2: 0,650).
> 2. É a mais **estável** em todos os experimentos.
> 3. Funciona em português sem dependência de modelos jurídicos específicos (ao contrário do BERTimbau-Legal).
>
> Alternativa: usar **BERTimbau** (`rufimelo/Legal-BERTimbau-sts-large-ma-v3`) como base, dado que é especializado em texto jurídico-normativo. Reportar **as duas variantes** (com Multilingual e com BERTimbau) e discutir diferenças no capítulo de Resultados.
>
> O **threshold = 0,7** deve ser justificado no texto: pode-se rodar uma análise de sensibilidade variando o limiar de 0,5 a 0,9 em incrementos de 0,05 e mostrar a curva Precision-Recall no anexo.

#### 3.2.7 Pendências antes de re-rodar

- [ ] Criar `utils/validates/compute_classification_scores.py` com o módulo acima.
- [ ] Confirmar BERTimbau em `validate_n1n2.py` e `validate_n1n2n3.py`.
- [ ] Adicionar bloco de classificação nos 5 validadores (`validate_n1.py`, `validate_n2.py`, `validate_n3.py`, `validate_n1n2.py`, `validate_n1n2n3.py`).
- [ ] Atualizar `README.md` com a lista completa de métricas (7 similaridade + 4 classificação).
- [ ] Re-executar todas as validações e atualizar `resultados.md`.
- [ ] Adicionar ao texto da dissertação (capítulo Metodologia §3.7) a definição de TP/FP/FN/TN por nível e o threshold escolhido.
- [ ] Adicionar ao capítulo de Resultados (§4.4.4) a nova tabela de classificação por modelo e por experimento.

> **Sinergia com §5.1:** se o refactor de unificação dos validadores (5.1) for feito **antes** desta implementação, basta editar **um único lugar** em vez de cinco. **Recomendação: fazer 5.1 primeiro, 3.2 depois.**

### 🔴 3.3 Alinhamento por índice é frágil

**Problema.** `build_pairs` (em `utils/validates/build_pairs.py` e nas funções `build_pairs_n2`/`build_pairs_n3`) assume que `dataset.texts_n1[i]` corresponde a `predictions.texts_n1[i]`. Se o modelo produz **mais** ou **menos** sentenças que o referência, o alinhamento por índice destrói as métricas — uma sentença geral é comparada com a sentença errada.

**Como aplicar.** Implementar alinhamento por similaridade:
```python
# para cada par (target_list, predicted_list), construir matriz de similaridade SBERT
# e usar scipy.optimize.linear_sum_assignment (Hungarian) para encontrar o melhor pareamento
```
Sentenças não pareadas viram TN/FN/FP conforme contexto. Isso muda **drasticamente** as métricas atuais para modelos que geram contagem de sentenças diferente do referência (provável para Qwen e Alpaca).

### 🟡 3.4 Adicionar BERTScore e ROUGE

**Problema.** A pesquisa só usa similaridade *sentence-level*. BERTScore traz comparação token-a-token com embeddings contextuais e é a métrica padrão atual para geração de texto. ROUGE-L captura sobreposição de subsequências (útil para N1).

**Como aplicar.**
```bash
pip install bert-score rouge-score
```
Adicionar `compute_bertscore_scores.py` e `compute_rouge_scores.py` análogos aos existentes.

### 🟡 3.5 SBERT português atualmente é o "ult5-pt-small"

**Problema.** `tgsc/sentence-transformer-ult5-pt-small` é a versão pequena (descartada parametricamente). Discriminação fica baixa em pares semanticamente próximos.

**Como aplicar.** Trocar para uma das opções:
- `neuralmind/bert-base-portuguese-cased` (BERTimbau base via mean pooling)
- `rufimelo/Legal-BERTimbau-sts-large-ma-v3` — já está sendo usado como BERTimbau separado; pode-se manter SBERT/Multilingual e descartar `ult5-small`.

### 🟡 3.6 Adicionar repetição com seed para medir variância

**Problema.** Temperatura 0,1 ainda é estocástica. Cada execução pode gerar resultados diferentes em ±0,02 nas métricas. Os rankings entre modelos próximos (Mistral × Gemma × Llama em algumas métricas) podem ser inconclusivos.

**Como aplicar.**
- Rodar cada (modelo × experimento) **3 a 5 vezes**.
- Reportar média ± desvio-padrão.
- Aplicar teste de Wilcoxon para comparar pares de modelos.

### 🟡 3.7 Avaliar concordância humana

**Problema.** O dataset tem uma única "resposta correta" por norma; mas para normas ambíguas, múltiplas anotações são válidas (ex.: "uso público ou coletivo" pode ser Selection ou Aplicabilidade dependendo da leitura). Sem inter-annotator agreement, métricas baixas podem ser do dataset, não do modelo.

**Como aplicar.** Selecionar 20 normas, anotar com 2–3 especialistas, calcular Cohen's kappa.

### 🟢 3.8 Permitir respostas em formato de "auto-correção"

**Problema.** Quando `parse_properties` retorna empty (JSON malformado), `generate_n3.py` tenta de novo do zero (até 3×). Para modelos pequenos, todas as 3 tentativas podem falhar com o mesmo erro de formatação.

**Como aplicar.** Na 2ª e 3ª tentativa, incluir a saída anterior no prompt e pedir correção:
```
Sua resposta anterior foi inválida ({erro}). Corrija o JSON mantendo o conteúdo:
{resposta_anterior}
```

---

## 4. Pesquisa — escopo e dataset

### 🔴 4.1 Dataset com 79 normas é estatisticamente pequeno

**Problema.** Para 6 modelos × 3 experimentos × ~7 métricas, 79 amostras geram intervalos de confiança largos. Diferenças entre Llama (0,716) e Dolphin (0,676) podem não ser significativas.

**Como aplicar.**
- Ampliar o dataset para 200–500 normas (NBR 9050 inteira, NBR 14718, NBR 15575, normas de incêndio).
- Aproveitar pelo menos NBR 9050 completa, que tem ~300 cláusulas.
- Pode-se usar GPT-4 para anotar massivamente e revisar manualmente apenas 20% (active learning).

### 🟡 4.2 Documentar overlap entre exemplos do prompt e dataset

**Problema.** Vários exemplos dos prompts (`n1.txt`, `n2.txt`, `n3_*.txt`) usam normas como "uso público ou coletivo", "rotas acessíveis", "casas de máquinas" — que aparecem no dataset. Isso é *test contamination*.

**Como aplicar.**
- Verificar se os exemplos dos prompts são derivados de normas presentes em `dataset.json`.
- Se sim: criar um **dataset de validação separado** com normas que **não** aparecem nos prompts.
- Reportar separadamente: desempenho em normas vistas (com vazamento) vs. inéditas.

### 🟡 4.3 Comparar contra um *baseline* simples

**Problema.** Não há baseline não-LLM para contextualizar os números. Sem ele, "0,716 médio" não tem referência.

**Como aplicar.** Implementar um baseline regex/heurístico:
- N1: split por ponto-final + heurística de coordenadas ("e", "ou").
- N2: regex para palavras-gatilho ("deve", "devem", "necessitam" → Requisito; "para", "exceto" → Exceção).
- N3: dicionário de propriedades comuns mapeando objeto.
Reportar métricas do baseline para mostrar o ganho real do LLM.

### 🟡 4.4 Análise de erros qualitativa

**Problema.** As métricas dão um número agregado, mas não indicam *que tipo* de erro o modelo comete (e.g., omite Exceção; troca Aplicabilidade com Seleção; gera unidades inventadas).

**Como aplicar.** Selecionar 30 erros (5 por modelo no EN2) e categorizar manualmente em uma taxonomia (omissão, substituição, alucinação, formatação). Reportar matriz de confusão por operador.

### 🟡 4.5 Estudar trade-off qualidade × custo

**Problema.** Llama lidera qualidade mas é 50–100× mais lento que Dolphin. Para um trabalho aplicado, esse ratio importa.

**Como aplicar.** Adicionar uma métrica composta `qualidade / tempo` (por ex., F1 / segundos por sentença) e plotar em scatter plot 2D modelo×qualidade×tempo.

### 🟢 4.6 Testar variações de prompt (A/B)

**Problema.** Há um único prompt por nível. Não se sabe se uma alternativa funciona melhor.

**Como aplicar.** Definir 2–3 variantes por prompt e rodar em uma amostra de 20 normas. Reportar a melhor.

---

## 5. Código — limpeza e estrutura

### 🔴 5.1 Eliminar duplicação massiva nos `validate_*.py`

**Problema.** `validate_n1.py`, `validate_n2.py`, `validate_n3.py`, `validate_n1n2.py`, `validate_n1n2n3.py` têm ~280 linhas cada com **>90% de código idêntico** (carregamento de modelos, loop de métricas, agregação de averages). Manutenção é multiplicada por 5: adicionar Accuracy/Precision/Recall/F1 exige 5 edições.

**Como aplicar.** Refatorar para uma única função `run_validation(level, build_pairs_fn, dataset_path, predicts_dir, output_path)`. Cada `validate_<n>.py` vira um wrapper de ~10 linhas.

```python
# utils/validates/run_validation.py
def run_validation(level, build_pairs_fn, dataset_path, predicts_dir, output_path):
    ...

# validates/validate_n1.py
from utils.validates.run_validation import run_validation
from utils.validates.build_pairs_n1 import build_pairs_n1
run_validation("n1", build_pairs_n1, ...)
```

### 🔴 5.2 Centralizar a lista de modelos

**Problema.** A lista `["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]` e o mapeamento para `model_id` Ollama estão **duplicados em 7 lugares**:
- `generate_n1.py:32`, `generate_n2.py:38`, `generate_n3.py:57`
- `generate_n1n2.py:13–19`, `generate_n1n2n3.py:13–19`
- `utils/generates/run_generator.py:21–33`
- `utils/generates/generate_config.py:7–32`
- `validate_n1.py:32`, `validate_n2.py:73`, `validate_n3.py:92` (e n1n2/n1n2n3)

**Como aplicar.** Mover para `config/models.py`:
```python
MODELS = {
    "llama":   "llama3.3:latest",
    "alpaca":  "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
    "mistral": "cnmoro/mistral_7b_portuguese:q4_K_M",
    "dolphin": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
    "gemma":   "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
    "qwen":    "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m",
}
MODEL_NAMES = list(MODELS.keys())
```
Depois `from config.models import MODELS, MODEL_NAMES` em todos os scripts.

### 🟡 5.3 `reset_model.py` e `unload_model.py` são duplicatas

**Problema.** Ambos chamam `subprocess.run(["ollama", "stop", model_id], check=False)` — apenas a mensagem de erro difere.

**Como aplicar.** Manter apenas `unload_model.py` e remover `reset_model.py` (ou unificar com flag `silent`).

### 🟡 5.4 `tmp/functions/generate_n2.py` é órfão

**Problema.** Arquivo em `tmp/` que provavelmente é versão antiga.

**Como aplicar.** Apagar `tmp/` ou mover para `archive/` no `.gitignore`.

### 🟡 5.5 `generate_n1.py` tem assinatura diferente de `generate_n2/n3.py`

**Problema.** `generate_n1.py` recebe argumentos só via CLI (não aceita parâmetros diretos da função). Já `generate_n2.py` e `generate_n3.py` aceitam `input_path/output_path/model_id` como kwargs. Inconsistência impede reuso programático de N1 a partir de outros scripts.

**Como aplicar.** Padronizar a assinatura de `generate_n1` igual a `generate_n2`. Permitirá criar `generate_full_pipeline.py` sem subprocess.

### 🟡 5.6 `menu_generate.py` tem 12 `if/elif` repetitivos

**Problema.** Linhas 61–93 são `elif choice == "X": options[i] = (...)` repetidos.

**Como aplicar.**
```python
KEY_TO_INDEX_N = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4}
KEY_TO_INDEX_M = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5}
if choice in KEY_TO_INDEX_N:
    i = KEY_TO_INDEX_N[choice]
    options_n[i] = (options_n[i][0], options_n[i][1], not options_n[i][2])
elif choice in KEY_TO_INDEX_M:
    ...
```

### 🟡 5.7 `safetensors` não está em `requirements.txt`

**Problema.** `load_nilc_model.py:8` importa `safetensors.numpy.load_file`, mas `safetensors` não está listado em `requirements.txt`. A linha `safetensors` no requirements existe, mas `pip install safetensors` instala o pacote base — falta confirmar a sub-importação `safetensors.numpy`.

**Como aplicar.** Trocar por `pip install "safetensors[numpy]"` se necessário, ou adicionar `numpy` explicitamente.

### 🟡 5.8 Adotar `ruff` + `mypy`

**Problema.** AGENTS.md diz "no formatter or linter is configured". Há type hints em vários lugares mas inconsistentes.

**Como aplicar.**
```bash
pip install ruff mypy
ruff check .
mypy --strict utils/
```
Adicionar `pyproject.toml` mínimo.

### 🟢 5.9 Empacotar como módulo Python

**Problema.** Toda chamada `python generates/generate_n1.py` requer manipulação de `sys.path` (linhas 9–11 dos scripts). Empacotar elimina isso.

**Como aplicar.** Criar `setup.py` ou `pyproject.toml`, instalar em modo editável (`pip install -e .`), e chamar `python -m mestrado_rase.generates.n1`.

### 🟢 5.10 Substituir `subprocess` por chamada Python para Ollama

**Problema.** `ensure_model_installed`, `unload_model` e `reset_model` chamam o binário `ollama` via subprocess. Mais lento e mais frágil.

**Como aplicar.**
```python
import ollama
client = ollama.Client(host="http://localhost:11434")
client.pull(model_id)
client.delete(model_id)  # ou stop via HTTP
```

---

## 6. Reprodutibilidade

### 🔴 6.1 Pinning de versões e seed

**Problema.** `requirements.txt` não tem versões pinadas. Resultados publicados podem não reproduzir em 6 meses por upgrade silencioso de `sentence-transformers` ou `gensim`.

**Como aplicar.**
```bash
pip freeze > requirements.lock
```
Documentar no README qual usar para reproduzir.

### 🔴 6.2 Persistir prompt e config junto da predição

**Problema.** `predicts/generate_<n>_<modelo>.json` salva apenas `counts`, `time`, `datas`. Não salva: hash do prompt usado, seed, temperatura, model_id, versão do código. Em 6 meses, ninguém saberá com qual versão foi gerado.

**Como aplicar.** Adicionar um bloco `meta` no topo de cada JSON:
```json
"meta": {
  "model_id": "llama3.3:latest",
  "temperature": 0.1,
  "top_p": 0.9,
  "repeat_penalty": 1.1,
  "seed": 42,
  "prompt_sha256": "abcd1234...",
  "code_git_sha": "..."
}
```

### 🟡 6.3 Fixar seed do Ollama

**Problema.** Sem seed, mesmo com temperatura baixa há variância entre runs.

**Como aplicar.** Passar `seed=42` no `OllamaLLM(...)` (parâmetro `model_kwargs={"seed": 42}` ou via Ollama API direta).

### 🟡 6.4 Dockerfile

**Problema.** Reproduzir exige instalar Python 3.11.9 + Ollama + 6 modelos + baixar embeddings.

**Como aplicar.** Criar `Dockerfile` com tudo pré-instalado e um `docker-compose.yml` com Ollama como serviço.

---

## 7. Bugs / problemas funcionais

### 🔴 7.1 `compute_tfidf_scores` recalcula vocabulário por par

**Problema.** Não é bug, mas combinado com 1.3 vira refactor obrigatório. O `vectorizer` é treinado em `valid_targets + valid_predictions` por chamada de função, ou seja, a cada modelo. OK para resultados, mas inconsistente: o vocabulário muda entre modelos. Para comparar modelos em pé de igualdade, vocabulário deveria ser fixo.

**Como aplicar.** Fitar o `TfidfVectorizer` uma vez no dataset de referência (`dataset.json` agregado) e apenas `transform` predições.

### 🟡 7.2 `normalize_field_name` tem branch inalcançável

**Problema.** Em `utils/n2/normalize_field_name.py:8-9`:
```python
if field == "selecao":
    return "selecao"
```
Após `unicodedata.normalize` + `lower`, "seleção" vira "selecao". A linha está correta, mas é redundante (qualquer match cai no `return field` final).

**Como aplicar.** Eliminar; manter apenas o branch das variantes "execao/excecao/execcao" (que é o que de fato precisa de normalização).

### 🟡 7.3 N3 retorna `type: "execcao"` (com cc)

**Problema.** `generate_n3.py:42` mapeia `"exception" → "execcao"` (com `cc` duplicado), enquanto o N2 (`process_text.py:9`) usa `"execao"` (com `c` simples). Inconsistência interna.

**Como aplicar.** Decidir uma grafia (preferencialmente `excecao`, com cedilha removida) e padronizar em todo o código + dataset + prompts.

### 🟡 7.4 `split_sentences` regex pode falhar em abreviações

**Problema.** `(?<!\b[A-Z])\.\s+(?![a-z])` em `utils/n1/split_sentences.py:16` tenta evitar quebrar em iniciais ("J. Silva"), mas falha em "etc.", "Sr.", "Dr.", "Fig.", "art.".

**Como aplicar.** Usar `nltk.tokenize.sent_tokenize` com modelo português:
```python
import nltk; nltk.download("punkt_tab")
from nltk.tokenize import sent_tokenize
parts = sent_tokenize(line, language="portuguese")
```

### 🟢 7.5 Heartbeat fixo em 60s

**Problema.** `invoke_with_timeout(..., 600.0, 60.0, log)` está hardcoded em N1/N2/N3 (`60.0` é o intervalo de heartbeat). Para Llama, são 1.5+ horas de execução com heartbeat só a cada 60s — parece travado entre os logs.

**Como aplicar.** Tornar configurável via env var ou reduzir para 30s.

### 🟢 7.6 `process_text` em N2 acumula linha-extra com espaço inicial

**Problema.** `utils/n2/process_text.py:38`: `resultado[campo_atual] += " " + linha.strip()` — quando o valor inicial é `""`, gera `" texto"` com espaço no começo.

**Como aplicar.** O `.strip()` final na linha 40 corrige no resultado, mas trocar por:
```python
if resultado[campo_atual]:
    resultado[campo_atual] += " " + linha.strip()
else:
    resultado[campo_atual] = linha.strip()
```

---

## 8. Gestão de execução

### 🔴 8.1 Resumir execuções interrompidas

**Problema.** Se `generate_n3.py` para no meio (timeout, GPU OOM), o `output_path` tem N processados. Re-rodar começa do zero, descartando trabalho.

**Como aplicar.** No início, ler `output_path` se existir, contar quantos `datas` têm, e pular esses no loop. Combinar com 1.7 (checkpoint append-only).

### 🔴 8.2 Paralelizar modelos quando há recursos

**Problema.** `run_generator` itera modelos sequencialmente com `subprocess.run` síncrono. Em uma máquina com GPU única, paralelizar não ajuda (Ollama serializa). Mas se houver duas GPUs ou Ollama remoto, sequencial é desperdício.

**Como aplicar.** Usar `concurrent.futures.ThreadPoolExecutor(max_workers=N)` com clientes Ollama apontando para hosts diferentes via env `OLLAMA_HOST`.

### 🟡 8.3 Logging estruturado

**Problema.** `init_log` escreve linhas `[YYYY-MM-DD HH:MM:SS] msg` em arquivo. Para análise posterior, não é parseável por jq.

**Como aplicar.** Trocar para JSON Lines:
```python
log_file.write(json.dumps({"ts": time.time(), "msg": message, "level": "info"}) + "\n")
```

### 🟡 8.4 Saída final por sumário em CSV/Markdown

**Problema.** As médias estão em JSON dentro de `metrics/`. Para a dissertação, é necessário gerar tabelas LaTeX manualmente.

**Como aplicar.** Adicionar `tools/generate_tables.py` que lê todos os `metrics/validate_*.json` e produz:
- `tables/results_en1.tex` (LaTeX tabular)
- `tables/results_en2.tex`
- `tables/results_en1n2.tex`
- `tables/timings.tex`
- `tables/summary.csv`

---

## 9. Documentação

### 🟡 9.1 README está desatualizado

**Problema.** `README.md:22` ainda diz que o objetivo "explora técnicas avançadas de Engenharia de Prompt, Fine-Tuning e Recuperação Aumentada por Geração (RAG)". Mas o código só implementa Engenharia de Prompt.

**Como aplicar.** Reescrever o objetivo no README para refletir o escopo real (alinhar com `plan.md`).

### 🟡 9.2 Documentar variáveis de ambiente

**Problema.** `GENERATE_DEBUG` é checada em vários scripts mas não documentada.

**Como aplicar.** Adicionar seção `## Environment variables` no README listando: `GENERATE_DEBUG`, `OLLAMA_HOST`, etc.

### 🟢 9.3 Documentar a estrutura do dataset

**Problema.** A estrutura JSON aninhada (datas → texts_n1 → operators_n2 → properties_n3) não é trivial; entender exige abrir o arquivo.

**Como aplicar.** Criar `docs/dataset_schema.md` com diagrama JSON Schema.

---

## 10. Checklist consolidada por prioridade

### 🔴 Implementar primeiro (alto impacto)

- [ ] **1.1** Carregar modelos de embedding uma vez para todos os validadores.
- [ ] **1.2** Vetorizar SBERT/BERTimbau/Multilingual.
- [ ] **1.3** Vetorizar TF-IDF.
- [ ] **1.4** Eliminar `subprocess` por modelo no `run_generator`.
- [ ] **1.5** Combinar as 4 chamadas de N3 em uma só.
- [ ] **2.1** Iterar modelo por modelo nos validadores.
- [ ] **2.2** Separar `averages` (no JSON principal) de `items` (em JSONL).
- [ ] **3.1** **Trocar FastText inglês por português (resultado WMD_ft atual é inválido).**
- [ ] **3.2** Implementar Accuracy/Precision/Recall/F1.
- [ ] **3.3** Alinhamento por similaridade (Hungarian) em vez de por índice.
- [ ] **4.1** Ampliar dataset.
- [ ] **5.1** Refatorar duplicação dos `validate_*.py`.
- [ ] **5.2** Centralizar lista de modelos em `config/models.py`.
- [ ] **6.1** Pinning de versões (`requirements.lock`).
- [ ] **6.2** Persistir meta (prompt hash, seed, model_id) junto da predição.
- [ ] **8.1** Resumir execuções interrompidas.
- [ ] **8.2** Paralelizar quando há múltiplos hosts Ollama.

### 🟡 Implementar a seguir (médio impacto)

- [ ] **1.6** `thread.join(timeout=...)` em vez de polling.
- [ ] **1.7** Checkpoint append-only.
- [ ] **2.3** Filtrar vocabulário NILC.
- [ ] **2.4** `torch.cuda.empty_cache()`.
- [ ] **3.4** Adicionar BERTScore + ROUGE.
- [ ] **3.5** Trocar SBERT pequeno por modelo maior.
- [ ] **3.6** Múltiplas execuções com seed para variância.
- [ ] **3.7** Inter-annotator agreement.
- [ ] **4.2** Garantir não-overlap entre prompts e dataset.
- [ ] **4.3** Baseline regex.
- [ ] **4.4** Análise qualitativa de erros.
- [ ] **4.5** Métrica composta qualidade × tempo.
- [ ] **5.3** Unificar `reset_model` e `unload_model`.
- [ ] **5.4** Apagar `tmp/`.
- [ ] **5.5** Padronizar assinatura de `generate_n1`.
- [ ] **5.6** Refatorar `menu_generate.py`.
- [ ] **5.7** Confirmar dependência `safetensors[numpy]`.
- [ ] **5.8** Adotar `ruff`/`mypy`.
- [ ] **6.3** Fixar seed do Ollama.
- [ ] **6.4** Dockerfile.
- [ ] **7.1** Vocabulário TF-IDF fixo.
- [ ] **7.2** Remover branch redundante em `normalize_field_name`.
- [ ] **7.3** Padronizar grafia "execao" / "excecao" / "execcao".
- [ ] **7.4** `nltk.sent_tokenize` para split.
- [ ] **8.3** Logging em JSON Lines.
- [ ] **8.4** `tools/generate_tables.py` para gerar tabelas LaTeX.
- [ ] **9.1** Atualizar README.
- [ ] **9.2** Documentar env vars.

### 🟢 Implementar quando possível (baixo impacto)

- [ ] **1.9** Substituir `langchain_ollama` por `ollama` direto.
- [ ] **3.8** Auto-correção de JSON malformado em N3.
- [ ] **4.6** A/B de prompts.
- [ ] **5.9** Empacotar como módulo Python.
- [ ] **5.10** API HTTP do Ollama em vez de subprocess.
- [ ] **7.5** Heartbeat configurável.
- [ ] **7.6** Concatenação correta no `process_text` N2.
- [ ] **9.3** Documentar schema do dataset.

---

## 11. Estimativa de ganhos esperados

| Otimização | Tempo total estimado (Llama N1N2N3) | Notas |
|---|---|---|
| **Hoje (baseline)** | ~9.450 s (2h37) | Conforme `resultados.md` |
| 1.5 (N3 unificado) | ~5.500 s (1h32) | -42% |
| 1.4 (sem subprocess) | -120 s adicionais (cumulativo) | -1% |
| 1.6 (join vs sleep) | desprezível | |
| 1.2 + 1.3 (vetorização nas validações) | -10 a -20 min nas validações | Não afeta geração |
| **Após 1.5+1.4+vetorização** | **~5.300 s (1h28)** | -44% no Llama |

| Memória (validate completo) | Antes | Depois |
|---|---|---|
| Modelos de embedding | ~5 GB pico | ~5 GB pico (carregar 1×, era 5×) |
| `metrics/validate_n3.json` | dezenas de MB | <1 MB (só averages) |
| NILC | ~600 MB | ~50 MB (filtrado) |

| Qualidade dos resultados | Antes | Depois |
|---|---|---|
| WMD_ft | inválido (inglês) | válido (português) |
| Accuracy/Precision/Recall/F1 | ausente | adicionado |
| Significância estatística | sem teste | Wilcoxon entre modelos |
| Alinhamento de pares | por índice | por similaridade |

---

## 12. Como começar

Sequência recomendada para implementar sem quebrar nada:

1. Criar `config/models.py` (5.2) — pré-requisito de muitas outras refatorações.
2. Aplicar 5.1 (refatoração dos validadores) — base para 1.1, 2.1, 3.2.
3. Aplicar 1.2 e 1.3 (vetorização) — ganho rápido e seguro.
4. Trocar FastText (3.1) — corrige resultado fundamentalmente errado.
5. Implementar Accuracy/Precision/Recall/F1 (3.2) — necessário para a dissertação.
6. Re-rodar todas as validações; atualizar tabelas em `resultados.md`.
7. Combinar chamadas N3 (1.5) — economia grande de tempo para próximas iterações.
8. Demais itens conforme cronograma.
