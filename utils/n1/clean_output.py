import re


def clean_output(text: str) -> str:
    cleaned = text.strip().replace("```", "")
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

    lines = []
    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.match(r"(?i)^texto_(inicio|fim)$", line):
            continue
        if re.match(r"(?i)^entrada\s*:", line):
            continue
        line = re.sub(r"(?i)^(resposta|saida|saída)\s*:\s*", "", line)
        line = line.strip().strip('"').strip("'").strip()
        if not line:
            continue
        lines.append(line)

    if lines:
        return "\n".join(lines)

    cleaned = re.sub(r"(?i)^(resposta|saida|saída)\s*:\s*", "", cleaned)
    return cleaned.strip().strip('"').strip("'").strip()
