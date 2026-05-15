"""Executa N geracoes com seeds diferentes e calcula desvio-padrao das metricas.

Uso:
    python tools/run_seed_sweep.py --level n2 --model mistral --seeds 42 43 44 \
        --out-dir runs/seed_sweep

Pre-requisitos: Ollama rodando e modelo ja baixado.
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Roda multiplas seeds e agrega metricas.")
    parser.add_argument("--level", choices=["n1", "n2", "n3"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument("--out-dir", default="runs/seed_sweep")
    parser.add_argument("--dataset", default="dataset.json")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    averages_per_seed: Dict[int, Dict[str, float]] = {}

    for seed in args.seeds:
        predict_out = out_dir / f"predict_{args.level}_{args.model}_seed{seed}.json"
        metric_out = out_dir / f"metric_{args.level}_{args.model}_seed{seed}.json"

        env = os.environ.copy()
        env["GEN_SEED"] = str(seed)

        print(f"=== Seed {seed}: gerando ===", flush=True)
        gen_cmd = [
            sys.executable,
            f"generates/generate_{args.level}.py",
            "--model", args.model,
            "--output", str(predict_out),
        ]
        rc = subprocess.run(gen_cmd, env=env, cwd=str(PROJECT_ROOT))
        if rc.returncode != 0:
            print(f"Geracao falhou para seed {seed}", flush=True)
            continue

        print(f"=== Seed {seed}: validando ===", flush=True)
        # Cria diretorio temporario com so este predict
        single_predicts = out_dir / f"predicts_seed{seed}"
        single_predicts.mkdir(exist_ok=True)
        link_path = single_predicts / f"generate_{args.level}_{args.model}.json"
        if link_path.exists():
            link_path.unlink()
        link_path.symlink_to(predict_out.resolve())

        val_cmd = [
            sys.executable,
            f"validates/validate_{args.level}.py",
            "--dataset", args.dataset,
            "--predicts", str(single_predicts),
            "--output", str(metric_out),
        ]
        rc = subprocess.run(val_cmd, env=env, cwd=str(PROJECT_ROOT))
        if rc.returncode != 0:
            print(f"Validacao falhou para seed {seed}", flush=True)
            continue

        with open(metric_out, "r", encoding="utf-8") as f:
            metric = json.load(f)
        averages = metric.get("averages", {}).get(args.model, {})
        flat: Dict[str, float] = {}
        for k, v in averages.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (int, float)):
                        flat[f"{k}.{sub_k}"] = float(sub_v)
            elif isinstance(v, (int, float)):
                flat[k] = float(v)
        averages_per_seed[seed] = flat

    # Agregado: media +/- desvio
    if not averages_per_seed:
        print("Sem dados para agregar.")
        return
    all_keys = sorted({k for d in averages_per_seed.values() for k in d.keys()})
    summary: Dict[str, Dict[str, float]] = {}
    for k in all_keys:
        values = [d[k] for d in averages_per_seed.values() if k in d]
        if not values:
            continue
        summary[k] = {
            "mean": statistics.fmean(values),
            "stdev": statistics.pstdev(values) if len(values) > 1 else 0.0,
            "n": len(values),
        }
    out_summary = out_dir / f"summary_{args.level}_{args.model}.json"
    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(
            {"seeds": list(averages_per_seed.keys()), "summary": summary},
            f, ensure_ascii=False, indent=2,
        )
    print(f"Sumario salvo em {out_summary}")
    for k, stats in summary.items():
        print(f"  {k}: {stats['mean']:.4f} +/- {stats['stdev']:.4f}  (n={stats['n']})")


if __name__ == "__main__":
    main()
