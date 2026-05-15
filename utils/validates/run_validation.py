import gc
import json
import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, List

import torch
from fuzzywuzzy import fuzz
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

from config.models import MODEL_NAMES
from utils.validates.compute_bertscore import compute_bertscore
from utils.validates.compute_classification_scores import (
    THRESHOLD_DEFAULT,
    compute_confusion_from_exact,
    compute_confusion_from_similarity,
    macro_average,
    metrics_from_confusion,
)
from utils.validates.compute_multilingual_scores import compute_multilingual_scores
from utils.validates.compute_rouge import compute_rouge_l
from utils.validates.compute_sbert_scores import compute_sbert_scores
from utils.validates.compute_tfidf_scores import compute_tfidf_scores, fit_tfidf_vectorizer
from utils.validates.compute_wmd_scores import compute_wmd_scores
from utils.validates.load_nilc_model import load_nilc_model, load_pt_fasttext


METRIC_NAMES: List[str] = [
    "fuzzywuzzy",
    "tfidf",
    "sbert",
    "bertimbau",
    "multilingual",
    "wmd_ft",
    "wmd_nilc",
    "bertscore",
    "rouge_l",
]


def _debug_enabled() -> bool:
    # Default ligado; setar GENERATE_DEBUG=0 silencia logs.
    env_debug: str = os.getenv("GENERATE_DEBUG", "1").strip().lower()
    return env_debug in {"1", "true", "yes", "on"}


def _bertscore_enabled() -> bool:
    raw = os.environ.get("VALIDATE_BERTSCORE", "1").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _rouge_enabled() -> bool:
    raw = os.environ.get("VALIDATE_ROUGE", "1").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def prepare_model_data(
    dataset: Dict[str, Any],
    predicts_dir: str,
    build_pairs_fn: Callable[[Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]],
    predicts_filename_prefix: str,
    label: str | None = None,
) -> Dict[str, Dict[str, Any]]:
    debug = _debug_enabled()
    model_data: Dict[str, Dict[str, Any]] = {}
    for model in MODEL_NAMES:
        input_path = Path(predicts_dir) / f"{predicts_filename_prefix}_{model}.json"
        if not input_path.exists():
            if debug:
                print(f"Pulando {model}: arquivo nao encontrado.", flush=True)
            continue
        suffix = f" ({label})" if label else ""
        print(f"Carregando modelo {model}{suffix}...", flush=True)
        with open(input_path, "r", encoding="utf-8") as file:
            predictions = json.load(file)
        pairs = build_pairs_fn(dataset, predictions)
        if debug:
            print(f"Pares gerados ({model}): {len(pairs)}", flush=True)
        targets = [p["target"] for p in pairs]
        predicted = [p["predicted"] for p in pairs]
        model_data[model] = {
            "pairs": pairs,
            "targets": targets,
            "predicted": predicted,
            "scores": {name: [] for name in METRIC_NAMES},
        }
    return model_data


def _apply_to_datasets(
    datasets: List[Dict[str, Dict[str, Any]]],
    metric_name: str,
    score_fn: Callable[[Dict[str, Any]], List[float | None]],
) -> None:
    for dataset in datasets:
        for model, data in dataset.items():
            scores = score_fn(data)
            data["scores"][metric_name] = scores
            print(f"Modelo {model}: {metric_name} validado.", flush=True)


def _fill_missing(datasets: List[Dict[str, Dict[str, Any]]], metric_name: str) -> None:
    for dataset in datasets:
        for model, data in dataset.items():
            data["scores"][metric_name] = [None] * len(data["targets"])
            print(f"Modelo {model}: {metric_name} indisponivel.", flush=True)


def _release_gpu() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _collect_vocab(datasets: List[Dict[str, Dict[str, Any]]]) -> set:
    vocab: set = set()
    for dataset in datasets:
        for data in dataset.values():
            for text in data.get("targets", []):
                for word in text.lower().split():
                    vocab.add(word.strip(".,;:!?\"'()[]{}"))
            for text in data.get("predicted", []):
                for word in text.lower().split():
                    vocab.add(word.strip(".,;:!?\"'()[]{}"))
    vocab.discard("")
    return vocab


def compute_all_scores(datasets: List[Dict[str, Dict[str, Any]]]) -> None:
    debug = _debug_enabled()

    _apply_to_datasets(
        datasets,
        "fuzzywuzzy",
        lambda d: [
            fuzz.partial_ratio(t, p) / 100.0
            for t, p in zip(d["targets"], d["predicted"])
        ],
    )

    corpus: List[str] = []
    for dataset in datasets:
        for data in dataset.values():
            corpus.extend(data.get("targets", []))
    tfidf_vec = fit_tfidf_vectorizer(corpus)
    _apply_to_datasets(
        datasets,
        "tfidf",
        lambda d: compute_tfidf_scores(d["targets"], d["predicted"], vectorizer=tfidf_vec),
    )

    sbert_repo = os.environ.get(
        "SBERT_MODEL", "tgsc/sentence-transformer-ult5-pt-small"
    )
    if debug:
        print(f"Carregando modelo SBERT ({sbert_repo})...", flush=True)
    sbert_model: SentenceTransformer = SentenceTransformer(sbert_repo)
    _apply_to_datasets(
        datasets,
        "sbert",
        lambda d: compute_sbert_scores(sbert_model, d["targets"], d["predicted"]),
    )
    del sbert_model
    gc.collect()
    _release_gpu()

    if debug:
        print("Carregando modelo BERTimbau...", flush=True)
    bertimbau_model: SentenceTransformer = SentenceTransformer(
        "rufimelo/Legal-BERTimbau-sts-large-ma-v3"
    )
    _apply_to_datasets(
        datasets,
        "bertimbau",
        lambda d: compute_sbert_scores(bertimbau_model, d["targets"], d["predicted"]),
    )
    del bertimbau_model
    gc.collect()
    _release_gpu()

    if debug:
        print("Carregando modelo MULTILINGUAL...", flush=True)
    multilingual_model: SentenceTransformer = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )
    _apply_to_datasets(
        datasets,
        "multilingual",
        lambda d: compute_multilingual_scores(
            multilingual_model, d["targets"], d["predicted"]
        ),
    )
    del multilingual_model
    gc.collect()
    _release_gpu()

    if debug:
        print("Carregando modelo WMD_FT (NILC FastText PT)...", flush=True)
    vocab = _collect_vocab(datasets)
    word_vectors_ft: KeyedVectors | None = load_pt_fasttext(vocab_whitelist=vocab)
    if word_vectors_ft is not None:
        _apply_to_datasets(
            datasets,
            "wmd_ft",
            lambda d: compute_wmd_scores(word_vectors_ft, d["targets"], d["predicted"]),
        )
        del word_vectors_ft
        gc.collect()
    else:
        _fill_missing(datasets, "wmd_ft")

    word_vectors_nilc: KeyedVectors | None = load_nilc_model(vocab_whitelist=vocab)
    if word_vectors_nilc is not None:
        _apply_to_datasets(
            datasets,
            "wmd_nilc",
            lambda d: compute_wmd_scores(
                word_vectors_nilc, d["targets"], d["predicted"]
            ),
        )
        del word_vectors_nilc
        gc.collect()
    else:
        print(
            "Modelo NILC nao encontrado em models/cbow_s300.txt ou src/models/cbow_s300.txt.",
            flush=True,
        )
        _fill_missing(datasets, "wmd_nilc")

    if _bertscore_enabled():
        if debug:
            print("Calculando BERTScore...", flush=True)
        _apply_to_datasets(
            datasets,
            "bertscore",
            lambda d: compute_bertscore(d["targets"], d["predicted"], lang="pt"),
        )
        _release_gpu()
    else:
        _fill_missing(datasets, "bertscore")

    if _rouge_enabled():
        if debug:
            print("Calculando ROUGE-L...", flush=True)
        _apply_to_datasets(
            datasets,
            "rouge_l",
            lambda d: compute_rouge_l(d["targets"], d["predicted"]),
        )
    else:
        _fill_missing(datasets, "rouge_l")


def _get_score(scores: List[Any], i: int) -> Any:
    return scores[i] if i < len(scores) else None


def compute_classification_metrics(
    model_data: Dict[str, Dict[str, Any]],
    level: str,
    base_metric: str = "multilingual",
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict[str, Dict[str, Any]]:
    classification: Dict[str, Dict[str, Any]] = {}
    for model, data in model_data.items():
        pairs = data["pairs"]
        targets = data["targets"]
        predicted = data["predicted"]
        sims = data["scores"].get(base_metric, [None] * len(pairs))

        if level == "n3" and pairs and isinstance(pairs[0].get("target_properties"), dict):
            target_props = [p.get("target_properties", {}) for p in pairs]
            predicted_props = [p.get("predicted_properties", {}) for p in pairs]
            per_field_conf = compute_confusion_from_exact(target_props, predicted_props)
            per_field_metrics = {
                f: metrics_from_confusion(c) for f, c in per_field_conf.items()
            }
            classification[model] = {
                "by_field": per_field_metrics,
                "macro": macro_average(per_field_metrics),
            }
            continue

        if level == "n2" and pairs and "operator" in pairs[0]:
            operators = sorted({p.get("operator", "") for p in pairs if p.get("operator")})
            per_op_metrics: Dict[str, Dict[str, float]] = {}
            for op in operators:
                idxs = [i for i, p in enumerate(pairs) if p.get("operator") == op]
                op_sims = [sims[i] if i < len(sims) else None for i in idxs]
                op_targets = [targets[i] for i in idxs]
                op_predicted = [predicted[i] for i in idxs]
                conf = compute_confusion_from_similarity(
                    op_sims, op_targets, op_predicted, threshold
                )
                per_op_metrics[op] = metrics_from_confusion(conf)
            overall_conf = compute_confusion_from_similarity(
                sims, targets, predicted, threshold
            )
            classification[model] = {
                "by_operator": per_op_metrics,
                "macro": macro_average(per_op_metrics),
                "overall": metrics_from_confusion(overall_conf),
            }
            continue

        conf = compute_confusion_from_similarity(sims, targets, predicted, threshold)
        classification[model] = {"overall": metrics_from_confusion(conf)}
    return classification


def build_metrics(
    model_data: Dict[str, Dict[str, Any]],
    level: str | None = None,
) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {"models": {}, "averages": {}}
    classification = (
        compute_classification_metrics(model_data, level) if level else {}
    )
    for model, data in model_data.items():
        pairs = data["pairs"]
        items: List[Dict[str, Any]] = []
        for i, pair in enumerate(pairs):
            entry: Dict[str, Any] = dict(pair)
            for name in METRIC_NAMES:
                entry[name] = _get_score(data["scores"][name], i)
            items.append(entry)

        averages: Dict[str, float | None] = {}
        for name in METRIC_NAMES:
            values = [
                item[name]
                for item in items
                if item[name] is not None and math.isfinite(item[name])
            ]
            averages[name] = sum(values) / len(values) if values else None

        model_metrics: Dict[str, Any] = {"counts": len(items), "items": items}
        if model in classification:
            model_metrics["classification"] = classification[model]
        metrics["models"][model] = model_metrics

        average_entry: Dict[str, Any] = dict(averages)
        if model in classification:
            macro = classification[model].get("macro") or classification[model].get(
                "overall"
            )
            if macro is not None:
                average_entry["classification_macro"] = {
                    k: macro[k] for k in ("accuracy", "precision", "recall", "f1")
                    if k in macro
                }
        metrics["averages"][model] = average_entry
    return metrics


def _split_items_enabled() -> bool:
    """Default ligado; setar METRICS_SPLIT_ITEMS=0 inclui items inline no JSON."""
    raw = os.environ.get("METRICS_SPLIT_ITEMS", "1").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def write_metrics(output_path: str | None, metrics: Dict[str, Any]) -> None:
    if not output_path:
        return
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not _split_items_enabled():
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(metrics, file, ensure_ascii=False, indent=2)
        return

    # Modo split: items em metrics/details/<base>_<modelo>.jsonl, JSON principal so com averages + classification.
    details_dir = Path(output_path).parent / "details"
    details_dir.mkdir(parents=True, exist_ok=True)
    base = Path(output_path).stem
    light: Dict[str, Any] = {"models": {}, "averages": metrics.get("averages", {})}
    for level_key in ("n1", "n2", "n3", "n1n2", "n1n2n3"):
        if level_key in metrics:
            light[level_key] = {
                "averages": metrics[level_key].get("averages", {}),
            }
    for model, payload in metrics.get("models", {}).items():
        light["models"][model] = {
            "counts": payload.get("counts", 0),
        }
        if "classification" in payload:
            light["models"][model]["classification"] = payload["classification"]
        items = payload.get("items", [])
        if items:
            details_file = details_dir / f"{base}_{model}.jsonl"
            with open(details_file, "w", encoding="utf-8") as f:
                for it in items:
                    f.write(json.dumps(it, ensure_ascii=False) + "\n")
            light["models"][model]["items_file"] = str(details_file.relative_to(Path(output_path).parent))
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(light, file, ensure_ascii=False, indent=2)


def run_validation(
    level: str,
    build_pairs_fn: Callable[[Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]],
    dataset_path: str,
    predicts_dir: str,
    output_path: str,
    predicts_filename_prefix: str | None = None,
) -> Dict[str, Any]:
    print(f"Validacao {level.upper()} iniciada.", flush=True)
    prefix = predicts_filename_prefix or f"generate_{level}"

    with open(dataset_path, "r", encoding="utf-8") as file:
        dataset: Dict[str, Any] = json.load(file)

    model_data = prepare_model_data(dataset, predicts_dir, build_pairs_fn, prefix)
    compute_all_scores([model_data])
    metrics = build_metrics(model_data, level=level)
    write_metrics(output_path, metrics)

    print(f"Resultado salvo em {output_path}", flush=True)
    if _debug_enabled():
        print(f"Validacao {level.upper()} finalizada.", flush=True)
    return metrics
