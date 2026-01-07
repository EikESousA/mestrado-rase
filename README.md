# Mestrado RASE

Este projeto gera dados RASE a partir de textos de normas, usando modelos LLM via Ollama.

## Estrutura rapida

- `main.py`: menu principal para gerar e validar dados.
- `generates/menu_generate.py`: menu de selecao de N e modelos.
- `dataset.json`: entrada de textos.
- `predicts/`: saida gerada.

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

## Saidas

Os arquivos gerados ficam em `predicts/` no formato:

- `predicts/generate_<n>_<modelo>.json`

Exemplos:

- `predicts/generate_n1_mistral.json`
- `predicts/generate_n1_llama.json`

Cada arquivo contem um JSON com `counts`, `time` e `datas` (com o texto original e os textos gerados). Se nenhum N ou modelo for selecionado, o menu informa o que falta.
