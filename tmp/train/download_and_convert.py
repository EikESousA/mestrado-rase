import json
import urllib.request
from datasets import load_dataset

def convert_pira():
    url = "https://raw.githubusercontent.com/C4AI/Pira/main/data/Pira-C.json"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)

    out = []
    for ex in data:
        out.append({
            "instruction": ex.get("question_pt_origin", ""),
            "input": ex.get("context_pt", ""),
            "output": ex.get("answer_pt", "")
        })

    with open("data/pira.jsonl", "w", encoding="utf-8") as f:
        for item in out:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("✅ Pirá convertido para data/pira.jsonl")

def convert_squad_br():
    ds = load_dataset("piEsposito/br-quad-2.0", split="train")
    with open("data/squad_br.jsonl", "w", encoding="utf-8") as f:
        for ex in ds:
            for qa in ex["qas"]:
                if qa["answers"]:
                    item = {
                        "instruction": qa["question"],
                        "input": ex["context"],
                        "output": qa["answers"][0]["text"]
                    }
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("✅ SQuAD-BR convertido para data/squad_br.jsonl")

if __name__ == "__main__":
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    convert_pira()
    convert_squad_br()
