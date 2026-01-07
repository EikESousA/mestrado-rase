import shutil
import subprocess


def install_ollama_linux() -> bool:
    installer: str | None = None
    if shutil.which("curl"):
        installer = "curl -fsSL https://ollama.com/install.sh | sh"
    elif shutil.which("wget"):
        installer = "wget -qO- https://ollama.com/install.sh | sh"

    if not installer:
        print("Erro: curl ou wget nao encontrado para instalar o Ollama.")
        return False

    print("Instalando o Ollama...")
    result: subprocess.CompletedProcess[str] = subprocess.run(installer, shell=True, check=False)
    return result.returncode == 0
