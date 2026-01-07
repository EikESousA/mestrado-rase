import shutil
import sys

from utils.generates.install_ollama_linux import install_ollama_linux


def check_ollama_installed() -> bool:
    if shutil.which("ollama"):
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
