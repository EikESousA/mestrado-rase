import unicodedata


def normalize_field_name(field: str) -> str:
    field = unicodedata.normalize("NFKD", field).encode("ASCII", "ignore").decode("ASCII")
    field = field.lower()

    if field in {"execao", "excecao", "execcao"}:
        return "execao"
    return field
