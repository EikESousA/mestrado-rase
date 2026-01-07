import re
from typing import Dict

from utils.n2.clean_output import clean_output
from utils.n2.normalize_field_name import normalize_field_name


def process_text(text: str) -> Dict[str, str]:
    campos = ["aplicabilidade", "selecao", "execao", "requisito"]
    resultado: Dict[str, str] = {campo: "" for campo in campos}

    cleaned: str = clean_output(text)
    padrao_campo = re.compile(r"^(.+?):\s*(.*)$", re.IGNORECASE)
    padrao_checagem = re.compile(rf"^({'|'.join(campos)}):$", re.IGNORECASE)

    campo_atual: str | None = None
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
