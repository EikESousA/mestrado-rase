#!/usr/bin/env bash
set -euo pipefail

HOST="${RASE_OLLAMA_HOST:-http://127.0.0.1:11435}"
MODELS_DIR="${RASE_OLLAMA_MODELS_DIR:-/usr/share/ollama/.ollama/models}"
HOST_NO_SCHEME="${HOST#http://}"
HOST_NO_SCHEME="${HOST_NO_SCHEME#https://}"

echo "Starting local Ollama CPU fallback on ${HOST_NO_SCHEME}"
echo "Using models from ${MODELS_DIR}"

export CUDA_VISIBLE_DEVICES=-1
export OLLAMA_LLM_LIBRARY="${OLLAMA_LLM_LIBRARY:-cpu_avx2}"
export OLLAMA_FLASH_ATTENTION=0
export OLLAMA_HOST="${HOST_NO_SCHEME}"
export OLLAMA_MODELS="${MODELS_DIR}"

exec /usr/local/bin/ollama serve
