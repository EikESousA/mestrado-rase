"""Configuracao do host Ollama.

Para usar o Ollama do Windows a partir do WSL/Linux, defina WINDOWS_HOST
com o IP e porta do Windows. Exemplos:

    WINDOWS_HOST = "192.168.0.10:11434"   # IP da maquina Windows na LAN
    WINDOWS_HOST = "172.28.0.1:11434"     # gateway do WSL2 (varia por boot)

Se WINDOWS_HOST for None ou vazio, o projeto usa o Ollama instalado
localmente. Caso nao esteja instalado, a instalacao automatica (Linux)
sera oferecida.

Para descobrir o IP do Windows a partir do WSL:
    ip route show default | awk '{print $3}'

No Windows, lembre de iniciar o Ollama escutando em todas as interfaces:
    setx OLLAMA_HOST "0.0.0.0:11434"
e liberar a porta 11434 no firewall.
"""
from __future__ import annotations

import os

WINDOWS_HOST: str | None = "172.19.80.1:11434"


def configured_host() -> str | None:
    """Retorna o host configurado normalizado (com esquema) ou None."""
    host = (WINDOWS_HOST or "").strip()
    if not host:
        return None
    if not host.startswith(("http://", "https://")):
        host = "http://" + host
    return host


def apply_to_env() -> str | None:
    """Espelha WINDOWS_HOST em OLLAMA_HOST se nao houver override no ambiente."""
    host = configured_host()
    if host and not os.environ.get("OLLAMA_HOST", "").strip():
        os.environ["OLLAMA_HOST"] = host
    return host
