import argparse
import sys
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from generates.generate_n2 import generate_n2

MODEL_CONFIG: Dict[str, str] = {
    "llama": "llama3.3:latest",
    "alpaca": "splitpierre/bode-alpaca-pt-br:13b-Q4_0",
    "mistral": "cnmoro/mistral_7b_portuguese:q4_K_M",
    "dolphin": "cnmoro/llama-3-8b-dolphin-portuguese-v0.3:4_k_m",
    "gemma": "brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
    "qwen": "cnmoro/Qwen2.5-0.5B-Portuguese-v1:q4_k_m",
}

template: str = """
Extrator RASE N2.
Use APENAS o Texto N1 para extrair os elementos. O Texto completo e apenas referencia.

Regras (ordem fixa):
1) aplicabilidade (opcional): onde/quando se aplica, sem verbos.
2) selecao (opcional): subconjunto da aplicabilidade, sem verbos.
3) execao (opcional): casos que NAO seguem a regra.
4) requisito (obrigatorio): acao/condicao principal, comeca com verbo.

Regras de saida:
- Retorne exatamente 4 linhas no formato abaixo.
- Cada campo deve aparecer no maximo uma vez.
- Se nao existir, use "" (string vazia).
- Nao adicione explicacoes, listas ou texto extra.

Exemplo (formato):
Texto completo:
"As areas ... Norma."
Texto N1:
"As areas de qualquer espaco ou edificacao de uso publico ou coletivo devem ser servidas de uma ou mais rotas acessiveis."
Resposta (4 linhas):
aplicabilidade: As areas de qualquer espaco ou edificacao
selecao: uso publico ou coletivo
execao: ""
requisito: devem ser servidas de uma ou mais rotas acessiveis

Agora processe:
Texto completo:
"{text}"
Texto N1:
"{text_n1}"

Resposta (4 linhas):
aplicabilidade:
selecao:
execao:
requisito:
"""


def generate_n1_n2() -> None:
    parser = argparse.ArgumentParser(description="Gerar operadores N2 a partir do N1.")
    parser.add_argument(
        "--model",
        choices=["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"],
        default="mistral",
        help="Modelo base para geracao.",
    )
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)
    parser.add_argument("--log", dest="log_path", default=None)
    args: argparse.Namespace = parser.parse_args()

    if args.model not in MODEL_CONFIG:
        print("Modelo invalido.")
        return

    input_path: str = f"predicts/generate_n1_{args.model}.json"
    output_path: str = f"predicts/generate_n1_n2_{args.model}.json"
    model_id: str = MODEL_CONFIG[args.model]

    if args.input_path:
        input_path = args.input_path
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_n2(
        input_path=input_path,
        output_path=output_path,
        model_id=model_id,
        log_path=args.log_path,
    )


if __name__ == "__main__":
    generate_n1_n2()
