import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Tuple

Tipo = Literal["n1", "n2", "n3"]
Modelo = Literal["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"]


def generate_config(tipo: Tipo, modelo: Modelo) -> Tuple[str, str, str]:
    input_file = "dataset.json"

    modelos = {
        "llama": {
            "output_file": f"predicts/generate_{tipo}_llama.json",
            "model": "llama3.3:latest",
        },
        "alpaca": {
            "output_file": f"predicts/generate_{tipo}_alpaca.json",
            "model": "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
        },
        "mistral": {
            "output_file": f"predicts/generate_{tipo}_mistral.json",
            "model": "cnmoro/mistral_7b_portuguese:q4_K_M",
        },
        "dolphin": {
            "output_file": f"predicts/generate_{tipo}_dolphin.json",
            "model": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
        },
        "gemma": {
            "output_file": f"predicts/generate_{tipo}_gemma.json",
            "model": "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
        },
        "qwen": {
            "output_file": f"predicts/generate_{tipo}_qwen.json",
            "model": "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m",
        },
    }

    output_file = modelos[modelo]["output_file"]
    model = modelos[modelo]["model"]

    return input_file, output_file, model


def get_active_names(options: List[tuple[str, bool]]) -> List[str]:
    return [name for name, active in options if active]


def wait_to_return() -> None:
    print()
    input("Digite qualquer tecla para voltar ao menu.")


def _install_ollama_linux() -> bool:
    installer = None
    if shutil.which("curl"):
        installer = "curl -fsSL https://ollama.com/install.sh | sh"
    elif shutil.which("wget"):
        installer = "wget -qO- https://ollama.com/install.sh | sh"

    if not installer:
        print("Erro: curl ou wget nao encontrado para instalar o Ollama.")
        return False

    print("Instalando o Ollama...")
    result = subprocess.run(installer, shell=True, check=False)
    return result.returncode == 0


def check_ollama_installed() -> bool:
    if shutil.which("ollama"):
        return True

    if sys.platform.startswith("linux"):
        if _install_ollama_linux():
            if shutil.which("ollama"):
                return True
            print("Ollama instalado, mas ainda nao esta no PATH.")
            print("Reinicie o terminal e tente novamente.")
            return False

    print("Erro: o Ollama nao esta instalado ou nao foi possivel instalar.")
    print("Instalacao manual:")
    print("curl -fsSL https://ollama.com/install.sh | sh")
    return False


def ensure_model_installed(model: str, model_id: str) -> bool:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erro: falha ao executar o Ollama.")
        return False

    if model_id in result.stdout:
        return True

    print(f"Modelo {model} nao encontrado. Instalando {model_id}...")
    pull = subprocess.run(["ollama", "pull", model_id], check=False)
    if pull.returncode != 0:
        print(f"Erro ao instalar o modelo {model_id}.")
        return False

    return True


def unload_model(model_id: str) -> None:
    try:
        subprocess.run(["ollama", "stop", model_id], check=False)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erro: falha ao descarregar o modelo.")


def run_generator(n_key: str, models: List[str]) -> None:
    if not check_ollama_installed():
        return

    script_path = Path(__file__).resolve().parent.parent / "generates" / f"generate_{n_key}.py"
    if not script_path.exists():
        print(f"N{n_key[1:]} nao esta disponivel neste menu.")
        return

    for model in models:
        model_id = None
        if model == "llama":
            model_id = "llama3.3:latest"
        elif model == "alpaca":
            model_id = "splitpierre/bode-alpaca-pt-br:13b-Q4_0"
        elif model == "mistral":
            model_id = "cnmoro/mistral_7b_portuguese:q4_K_M"
        elif model == "dolphin":
            model_id = "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m"
        elif model == "gemma":
            model_id = "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16"
        elif model == "qwen":
            model_id = "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m"


        if model_id and not ensure_model_installed(model, model_id):
            return

        print(f"Gerando {n_key.upper()} com {model}...")
        print()
        subprocess.run(
            [sys.executable, str(script_path), "--model", model],
            check=False,
        )
        if model_id:
            unload_model(model_id)


def reset_model(model_id: str, log: Callable[[str], None] | None = None) -> None:
    try:
        subprocess.run(["ollama", "stop", model_id], check=False)
    except (subprocess.SubprocessError, FileNotFoundError):
        if log is not None:
            log("Erro ao descarregar o modelo.")


def invoke_with_timeout(
    chain: Any,
    payload: Dict[str, str],
    timeout: float,
    heartbeat_interval: float,
    log: Callable[[str], None] | None = None,
) -> tuple[str | None, bool]:
    result_holder: Dict[str, str] = {}
    error_holder: Dict[str, Exception] = {}

    def _run() -> None:
        try:
            result_holder["result"] = chain.invoke(payload)
        except Exception as exc:
            error_holder["error"] = exc

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    start = time.time()
    next_heartbeat = start + heartbeat_interval
    while thread.is_alive():
        now = time.time()
        if now >= start + timeout:
            return None, True
        if heartbeat_interval > 0 and now >= next_heartbeat and log is not None:
            log(
                "Ainda aguardando resposta do modelo "
                f"({int(now - start)}s)..."
            )
            next_heartbeat = now + heartbeat_interval
        time.sleep(0.2)

    if "error" in error_holder:
        raise error_holder["error"]
    return result_holder.get("result"), False


def empty_properties_n3() -> Dict[str, str]:
    return {
        "type": "",
        "object": "",
        "property": "",
        "comparation": "",
        "target": "",
        "unit": "",
    }


def normalize_field_name(field: str) -> str:
    field = unicodedata.normalize("NFKD", field).encode("ASCII", "ignore").decode("ASCII")
    field = field.lower()

    if field == "selecao":
        return "selecao"
    if field in {"execao", "excecao", "execcao"}:
        return "execao"
    if field == "aplicabilidade":
        return "aplicabilidade"
    if field == "requisito":
        return "requisito"
    return field


def clean_n2_output(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"(?i)^(resposta|saida)\s*:\s*", "", cleaned)
    return cleaned.strip()


def process_n2_text(text: str) -> Dict[str, str]:
    campos = ["aplicabilidade", "selecao", "execao", "requisito"]
    resultado = {campo: "" for campo in campos}

    cleaned = clean_n2_output(text)
    padrao_campo = re.compile(r"^(.+?):\s*(.*)$", re.IGNORECASE)
    padrao_checagem = re.compile(rf"^({'|'.join(campos)}):$", re.IGNORECASE)

    campo_atual = None
    for linha in cleaned.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        match = padrao_campo.match(linha)
        if match:
            raw_field = match.group(1).strip()
            campo = normalize_field_name(raw_field)
            valor = match.group(2).strip()

            if campo not in resultado:
                continue

            if padrao_checagem.match(valor.lower()):
                valor = ""

            resultado[campo] = valor
            campo_atual = campo if valor == "" else None
        elif campo_atual:
            if not padrao_campo.match(linha):
                resultado[campo_atual] += " " + linha.strip()

    return {k: v.strip() for k, v in resultado.items()}


def build_operators_n2(result: Dict[str, str]) -> Dict[str, Any]:
    return {
        "requeriments": {
            "text_n2": result.get("requisito", ""),
            "properties_n3": empty_properties_n3(),
        },
        "aplicability": {
            "text_n2": result.get("aplicabilidade", ""),
            "properties_n3": empty_properties_n3(),
        },
        "selection": {
            "text_n2": result.get("selecao", ""),
            "properties_n3": empty_properties_n3(),
        },
        "exception": {
            "text_n2": result.get("execao", ""),
            "properties_n3": empty_properties_n3(),
        },
    }
