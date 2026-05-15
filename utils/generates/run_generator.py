import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List

from config.models import MODELS, predict_path
from utils.generates.check_ollama_installed import check_ollama_installed
from utils.generates.ensure_model_installed import ensure_model_installed
from utils.generates.unload_model import unload_model


_INPUT_BY_LEVEL: Dict[str, str] = {
    "n1": "dataset.json",
    "n2": "predicts/generate_n1_{model}.json",
    "n3": "predicts/generate_n2_{model}.json",
    "n1n2": "predicts/generate_n1_{model}.json",
    "n1n2n3": "predicts/generate_n1n2_{model}.json",
}


def _resolve_generator(n_key: str) -> Callable[..., None] | None:
    if n_key == "n1":
        from generates.generate_n1 import generate_n1
        return generate_n1
    if n_key in ("n2", "n1n2"):
        from generates.generate_n2 import generate_n2
        return generate_n2
    if n_key in ("n3", "n1n2n3"):
        from generates.generate_n3 import generate_n3
        return generate_n3
    return None


def _hosts() -> List[str]:
    raw = os.environ.get("OLLAMA_HOSTS", "").strip()
    if raw:
        return [h.strip() for h in raw.split(",") if h.strip()]
    single = os.environ.get("OLLAMA_HOST", "http://localhost:11434").strip()
    return [single]


def _run_one(
    generator: Callable[..., None],
    n_key: str,
    model: str,
    model_id: str,
    input_template: str,
    host: str,
) -> None:
    if not ensure_model_installed(model, model_id):
        return
    input_path = (
        "dataset.json" if input_template == "dataset.json"
        else input_template.format(model=model)
    )
    output_path = predict_path(n_key, model)
    print(f"[{host}] Gerando {n_key.upper()} com {model}...")
    # Para isolar geracoes por host, ajusta OLLAMA_HOST localmente.
    prev_host = os.environ.get("OLLAMA_HOST")
    os.environ["OLLAMA_HOST"] = host
    try:
        generator(input_path=input_path, output_path=output_path, model_id=model_id)
    except Exception as exc:
        print(f"[{host}] Erro durante {n_key} com {model}: {exc}")
    finally:
        try:
            unload_model(model_id)
        except Exception:
            pass
        if prev_host is None:
            os.environ.pop("OLLAMA_HOST", None)
        else:
            os.environ["OLLAMA_HOST"] = prev_host


def run_generator(n_key: str, models: List[str]) -> None:
    if not check_ollama_installed():
        return

    generator = _resolve_generator(n_key)
    if generator is None:
        print(f"N{n_key[1:]} nao esta disponivel neste menu.")
        return

    input_template = _INPUT_BY_LEVEL.get(n_key)
    if input_template is None:
        print(f"Nivel desconhecido: {n_key}")
        return

    hosts = _hosts()
    tasks: List[tuple[str, str]] = []
    for model in models:
        model_id = MODELS.get(model)
        if model_id is None:
            print(f"Modelo desconhecido: {model}")
            continue
        tasks.append((model, model_id))

    if not tasks:
        return

    if len(hosts) == 1:
        # Sequencial (Ollama serializa GPU local).
        for model, model_id in tasks:
            _run_one(generator, n_key, model, model_id, input_template, hosts[0])
        return

    # Distribui (model, model_id) entre hosts via round-robin com workers paralelos.
    max_workers = min(len(hosts), len(tasks))
    print(f"Distribuindo {len(tasks)} modelos em {len(hosts)} hosts Ollama...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, (model, model_id) in enumerate(tasks):
            host = hosts[i % len(hosts)]
            futures.append(
                executor.submit(
                    _run_one, generator, n_key, model, model_id, input_template, host
                )
            )
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as exc:
                print(f"Worker falhou: {exc}")
