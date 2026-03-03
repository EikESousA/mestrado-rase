import unicodedata


def normalize_field_name(field: str) -> str:
    field = unicodedata.normalize("NFKD", field).encode("ASCII", "ignore").decode("ASCII")
    field = field.lower().strip().strip(":")
    field = field.replace("-", " ").replace("_", " ")
    field = " ".join(field.split())

    aliases = {
        "selecao": "selecao",
        "selection": "selecao",
        "execao": "execao",
        "excecao": "execao",
        "execcao": "execao",
        "exception": "execao",
        "aplicabilidade": "aplicabilidade",
        "aplicability": "aplicabilidade",
        "requisito": "requisito",
        "requirement": "requisito",
        "requirements": "requisito",
        "requeriments": "requisito",
    }
    return aliases.get(field, field)
