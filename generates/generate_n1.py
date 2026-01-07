import argparse
from pathlib import Path

from utils.generate_n1_utils import generate_n1
from utils.generate_utils import generate_config


template = """
Voce e um reescritor. Transforme o texto em sentencas RASE N1.

Regras:
1) Quebre em sentencas curtas e diretas.
2) Cada sentenca deve ter uma unica regra computavel.
3) Nao invente elementos (aplicabilidade, selecao, requisito, excecao). Preserve apenas o que existir.
4) Nao adicione explicacoes, titulos, bullets, numeracao ou o texto original.
5) Saida: apenas as sentencas, uma por linha, terminadas com ponto final.

Exemplo:
Entrada:
A inclinacao transversal da superficie deve ser de ate 2 % para pisos internos e de ate 3 % para pisos externos.
Saida:
Pisos internos devem ter inclinacao transversal de no maximo 2%.
Pisos externos devem ter inclinacao transversal de no maximo 3%.

TEXTO_INICIO
{text}
TEXTO_FIM
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerar sentencas RASE N1.")
    parser.add_argument(
        "--model",
        choices=["llama", "alpaca", "mistral", "dolphin", "gemma", "qwen"],
        default="mistral",
        help="Modelo base para geracao.",
    )
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default=None)
    parser.add_argument("--log", dest="log_path", default=None)
    args = parser.parse_args()

    input_path, output_path, model_id = generate_config("n1", args.model)
    if args.input_path:
        input_path = args.input_path
    if args.output_path:
        output_path = args.output_path

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generate_n1(
        input_path=input_path,
        output_path=output_path,
        template=template,
        model=model_id,
        log_path=args.log_path,
    )


if __name__ == "__main__":
    main()
