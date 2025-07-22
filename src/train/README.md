# Treinamento LoRA para Chatbot RAG em Português

## 📋 Descrição

Este projeto treina modelos LoRA para fine-tuning leve usando diferentes modelos de linguagem:

- **Mistral 7B Instruct** quantizado em 4-bit (ideal para GPUs RTX 4070, 4080, 3060 e similares)
- **TinyLlama 3B** também com quantização 4-bit para GPUs menores
- **GPT-Neo 125M**, modelo leve para CPU (sem quantização), indicado para quem não tem GPU dedicada e quer respostas rápidas (2-3s)

O objetivo é criar um chatbot RAG (Retrieval-Augmented Generation) em português usando datasets Pirá e SQuAD-BR 2.0, com contexto manual e sem ElasticSearch.

---

## 🛠️ Requisitos

- Para Mistral 7B e TinyLlama 3B:
  - GPU Nvidia com pelo menos 12 GB de VRAM (RTX 3060, 4070, 4080 ou superior)
  - CUDA e drivers Nvidia atualizados
- Para GPT-Neo 125M:
  - CPU moderna (idealmente com múltiplos núcleos, ex. i5/i7 de última geração)
  - Roda sem GPU, porém com menor capacidade e velocidade menor para modelos maiores
- Python 3.10 ou 3.11
- Espaço em disco para datasets e checkpoints (~10 GB)
- Conexão com internet para baixar modelos e datasets

---

## 📦 Instalação

1. Clone o repositório ou copie os arquivos para sua máquina.

2. Crie e ative ambiente virtual Python (opcional, mas recomendado):

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows PowerShell
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🗂️ Preparar datasets

Baixe e converta os datasets Pirá e SQuAD-BR para JSONL com:

```bash
python download_and_convert.py
```

Os arquivos `pira.jsonl` e `squad_br.jsonl` serão criados na pasta `data/`.

---

## 🏋️‍♂️ Treinar o LoRA

O script `train_lora.py` foi adaptado para suportar diferentes modelos e configurações automáticas:

- **Modelos suportados**:
  - `mistral` (Mistral 7B 4-bit quantizado)
  - `tinyllama` (TinyLlama 3B 4-bit quantizado)
  - `gpt` (GPT-Neo 125M sem quantização, para CPU)

Execute o treino com:

```bash
python train_lora.py [modelo]
```

Exemplos:

```bash
python train_lora.py mistral
python train_lora.py tinyllama
python train_lora.py gpt
```

### Configurações automáticas

- Para Mistral e TinyLlama, o treino usa quantização 4-bit e `device_map="auto"` para usar GPU.
- Para GPT-Neo 125M, o modelo roda na CPU, sem quantização, com batch size e passos ajustados para menor uso de memória.
- As configurações de batch size, steps, fp16 etc são ajustadas automaticamente com base no modelo e na GPU detectada.

---

## 🤖 Inferência com LoRA treinado

O script `test_infer.py` (ou seu script customizado) deve ser adaptado para carregar o modelo base e o LoRA conforme o modelo escolhido:

- Para Mistral e TinyLlama, use quantização 4-bit com `BitsAndBytesConfig` e `device_map="auto"`.
- Para GPT-Neo 125M, carregue o modelo sem quantização e em CPU (`device_map="cpu"`).
- Envie os tensores para CUDA somente se GPU disponível e modelo grande.

Exemplo de comando para rodar inferência:

```bash
python test_infer.py [modelo]
```

---

## 📊 Monitorar uso de VRAM (opcional)

- Windows PowerShell:

```powershell
.	rain_monitor.bat
```

- Linux/bash:

```bash
./train_monitor.sh
```

Esses scripts ajudam a monitorar o uso da GPU e sugerem ajustes no batch size para evitar crashes por falta de memória.

---

## ⚙️ Notas importantes

- **Quantização 4-bit (bitsandbytes)** é usada somente para modelos grandes (Mistral 7B, TinyLlama 3B) para reduzir consumo de VRAM.
- **GPT-Neo 125M** não usa quantização, roda na CPU, é ideal para quem não tem GPU dedicada.
- Ajuste os parâmetros do treino conforme seu hardware para otimizar desempenho e evitar erros.
- Para produção, considere usar RAG com ElasticSearch ou outro indexador para melhorar contexto e respostas.

---

## 📂 Estrutura dos arquivos

```
├── data/
│   ├── pira.jsonl
│   └── squad_br.jsonl
├── lora_out/               # modelo LoRA treinado será salvo aqui
├── train_lora.py           # script de treino LoRA multi-modelo e multi-device
├── test_infer.py           # script para testar inferência adaptado para múltiplos modelos
├── download_and_convert.py # script para baixar e converter datasets
├── train_monitor.ps1       # monitor VRAM PowerShell Windows
├── train_monitor.sh        # monitor VRAM Bash Linux
├── train_monitor.bat       # monitor VRAM básico Windows cmd
├── requirements.txt        # dependências Python
└── README.md               # este arquivo
```

---

## 💡 Dicas

- Sempre monitore a VRAM para ajustar batch size e evitar crashes.
- Use 4-bit para balancear qualidade e desempenho em GPUs.
- Em CPU, prefira modelos leves como GPT-Neo 125M para respostas rápidas (2-3s).
- Adapte o prompt e o dataset conforme seu caso para melhorar resultados.

---

Se precisar, posso ajudar a criar um guia de inferência com esses modelos também!

http://www.wikicfp.com/cfp/call?conference=computer%20science&page=2
https://ppgcc.github.io/discentesPPGCC/pt-BR/qualis/
