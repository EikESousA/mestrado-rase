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
- `predicts/`: saida gerada.
- `metrics/`: saida das validacoes.

## Requisitos

- Python 3.11+.
- Ollama instalado e em execucao (`ollama serve`).
- Modelos serao baixados automaticamente pelo menu (quando necessario).

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

No menu, escolha "Gerar dados" e selecione o N (n1/n2/n3) e o modelo. O sistema usara `dataset.json` como entrada.

## Funcionalidades (N1/N2)

### Geracao N1

`generates/generate_n1.py` transforma os textos de `dataset.json` em sentencas N1 usando o prompt `prompts/n1.txt`. Cada entrada gera:

- `texts_n1`: lista com `text_n1` e `operators_n2` vazio (estrutura base para N2).
- Metadados: `counts` e `time`.

### Geracao N2

`generates/generate_n2.py` preenche os operadores N2 a partir das sentencas N1. Ele espera um arquivo com `texts_n1` (normalmente a saida do N1) e usa o prompt `prompts/n2.txt`.

### Validacao N1

`validates/validate_n1.py` compara as sentencas N1 geradas com o `dataset.json` e grava metricas em `metrics/validate_n1.json`. Sao usadas:

- FuzzyWuzzy (similaridade parcial)
- TF-IDF
- SBERT (pt)
- SentenceTransformer multilingual
- WMD (FastText e NILC, quando disponiveis)

## Saidas

Os arquivos gerados ficam em `predicts/` no formato:

- `predicts/generate_<n>_<modelo>.json`

Exemplos:

- `predicts/generate_n1_mistral.json`
- `predicts/generate_n1_llama.json`

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

## Validacoes

Os arquivos de validacao ficam em `metrics/` (ex: `metrics/validate_n1.json` e `metrics/validate_n2.json`).

Cada arquivo de validacao possui:

- `models`: resultados detalhados por modelo, contendo `counts` e `items`.
- `averages`: medias agregadas por modelo para cada metrica.

Em `models.<modelo>.items`, cada item inclui:

- Indices (`text_index`, `sentence_index`) e, no N2, o `operator`.
- `text`: texto original completo.
- `text_n1`: sentenca N1 correspondente (no N2).
- `target`: texto de referencia do dataset.
- `predicted`: texto gerado pelo modelo.
- `fuzzywuzzy`, `tfidf`, `sbert`, `multilingual`, `wmd_ft`, `wmd_nilc`: scores por par (0 a 1 quando aplicavel).

Interpretacao dos scores:

- `fuzzywuzzy`: similaridade parcial por caracteres.
- `tfidf`: similaridade cosseno em TF-IDF.
- `sbert`: similaridade semantica com SBERT pt.
- `multilingual`: similaridade semantica multilingue.
- `wmd_ft`: similaridade derivada do Word Mover's Distance com FastText.
- `wmd_nilc`: similaridade derivada do Word Mover's Distance com NILC (quando disponivel).

Os valores em `averages` sao medias simples de cada metrica, ignorando valores ausentes. Quanto mais proximo de 1, maior a similaridade entre `target` e `predicted` em todas as metricas, incluindo WMD (que ja e normalizado).

## Ajuda

Se você tiver dúvidas, relatórios de bugs ou solicitações de recursos, não hesite em nos mandar mensagem para o email **eike.sousa@hotmail.com**.

Lembre-se de seguir nosso **[Código de Conduta](https://github.com/EikESousA/IAnvisa/blob/main/CODE_OF_CONDUCT.md)**.

## Licença

Licenciado pelo CC0-1.0 license. Consulte o arquivo **[LICENSE](https://github.com/EikESousA/IAnvisa/blob/main/LICENSE)** para obter detalhes.
