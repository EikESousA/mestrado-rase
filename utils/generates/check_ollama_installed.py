import os
import shutil
import sys
import urllib.error
import urllib.request

from config.ollama import apply_to_env
from utils.generates.install_ollama_linux import install_ollama_linux


def _probe_remote(host: str, timeout: float = 2.0) -> bool:
    url = host.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return 200 <= resp.status < 500
    except (urllib.error.URLError, ConnectionError, OSError):
        return False


def check_ollama_installed() -> bool:
    # Se WINDOWS_HOST estiver configurado em config/ollama.py, espelha em OLLAMA_HOST.
    apply_to_env()

    host: str = os.environ.get("OLLAMA_HOST", "").strip()
    if host:
        if not host.startswith(("http://", "https://")):
            host = "http://" + host
        if _probe_remote(host):
            print(f"Usando Ollama remoto em {host}.")
            return True
        print(f"Erro: nao foi possivel falar com o Ollama em {host}.")
        print("Verifique se o servico esta rodando e acessivel.")
        return False

    ollama_path: str | None = shutil.which("ollama")
    if ollama_path:
        return True

    if sys.platform.startswith("linux"):
        if install_ollama_linux():
            if shutil.which("ollama"):
                return True
            print("Ollama instalado, mas ainda nao esta no PATH.")
            print("Reinicie o terminal e tente novamente.")
            return False

    print("Erro: o Ollama nao esta instalado ou nao foi possivel instalar.")
    print("Instalacao manual:")
    print("curl -fsSL https://ollama.com/install.sh | sh")
    return False
