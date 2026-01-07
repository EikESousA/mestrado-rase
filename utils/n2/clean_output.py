import re


def clean_output(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("```", "")
    cleaned = re.sub(r"(?i)^(resposta|saida)\s*:\s*", "", cleaned)
    return cleaned.strip()
