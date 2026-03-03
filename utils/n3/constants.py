from pathlib import Path


PROMPT_PATHS = {
    "aplicability": Path("prompts") / "n3_aplicabilidade.txt",
    "selection": Path("prompts") / "n3_selecao.txt",
    "exception": Path("prompts") / "n3_execao.txt",
    "requeriments": Path("prompts") / "n3_requisito.txt",
}

PROMPT_INPUT_KEYS = {
    "aplicability": "aplicabilidade",
    "selection": "selecao",
    "exception": "execao",
    "requeriments": "requisito",
}

TYPE_BY_OPERATOR = {
    "aplicability": "aplicabilidade",
    "selection": "selecao",
    "exception": "execcao",
    "requeriments": "requisito",
}
