"""Calcula metrica composta qualidade/tempo (F1 / segundos por sentenca) e gera CSV.

Le os predicts (campo `time` e `counts`) e os metrics (F1 macro de classificacao).
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict


def _safe_get(d: dict, *keys, default=None):
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
        if d is None:
            return default
    return d


def main() -> None:
    parser = argparse.ArgumentParser(description="Calcula F1/segundo por modelo.")
    parser.add_argument("--metrics", default="metrics/validate_n2.json")
    parser.add_argument("--predicts-dir", default="predicts")
    parser.add_argument("--level", default="n2")
    parser.add_argument("--out", default="tables/quality_time.csv")
    args = parser.parse_args()

    with open(args.metrics, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    averages = metrics.get("averages", {})
    rows = []
    for model, avg in averages.items():
        f1 = _safe_get(avg, "classification_macro", "f1", default=None)
        predict_path = Path(args.predicts_dir) / f"generate_{args.level}_{model}.json"
        if not predict_path.exists():
            print(f"Pulando {model}: predict nao encontrado")
            continue
        with open(predict_path, "r", encoding="utf-8") as f:
            predict = json.load(f)
        total_time = float(predict.get("time", 0.0))
        n_sentences = sum(
            len(item.get("texts_n1", []))
            for item in predict.get("datas", [])
        )
        if n_sentences == 0:
            continue
        sec_per_sentence = total_time / n_sentences
        ratio = (f1 / sec_per_sentence) if (f1 and sec_per_sentence > 0) else None
        rows.append({
            "model": model,
            "f1": f1,
            "total_time_s": total_time,
            "sentences": n_sentences,
            "sec_per_sentence": sec_per_sentence,
            "f1_per_second": ratio,
        })

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        if not rows:
            print("Nenhum dado para escrever.")
            return
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["f1_per_second"] or 0), reverse=True):
            writer.writerow(row)
    print(f"CSV salvo em {args.out}")
    for row in rows:
        if row["f1_per_second"]:
            print(f"  {row['model']}: F1={row['f1']:.3f} t/sent={row['sec_per_sentence']:.3f}s F1/s={row['f1_per_second']:.4f}")


if __name__ == "__main__":
    main()
