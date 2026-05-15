"""Alinhamento por similaridade (Hungarian) para corrigir 3.3 do otimize.md.

Quando `len(targets) != len(predicted)`, alinhamento por indice destroi as metricas.
Esta funcao usa SBERT multilingual + linear_sum_assignment para encontrar o melhor
pareamento; sentencas nao pareadas viram FN (target sem predito) ou FP (predito sem target).
"""

import os
from functools import lru_cache
from typing import Iterable, List, Tuple


def _enabled() -> bool:
    """Default ligado; setar VALIDATE_HUNGARIAN=0 reverte para alinhamento por indice."""
    raw = os.environ.get("VALIDATE_HUNGARIAN", "1").strip().lower()
    return raw in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def _aligner_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )


def align_lists(
    targets: List[str],
    predicted: List[str],
) -> List[Tuple[int | None, int | None]]:
    """Retorna lista de pares (i_target, i_pred). None de um lado = nao pareado.

    Sem dependencia ativa (sem env var), retorna alinhamento por indice.
    """
    if not _enabled():
        n = max(len(targets), len(predicted))
        return [
            (i if i < len(targets) else None, i if i < len(predicted) else None)
            for i in range(n)
        ]

    if not targets and not predicted:
        return []
    if not predicted:
        return [(i, None) for i in range(len(targets))]
    if not targets:
        return [(None, j) for j in range(len(predicted))]

    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        import torch
    except ImportError:
        n = max(len(targets), len(predicted))
        return [
            (i if i < len(targets) else None, i if i < len(predicted) else None)
            for i in range(n)
        ]

    model = _aligner_model()
    t_emb = model.encode(
        targets, convert_to_tensor=True, normalize_embeddings=True,
        batch_size=64, show_progress_bar=False,
    )
    p_emb = model.encode(
        predicted, convert_to_tensor=True, normalize_embeddings=True,
        batch_size=64, show_progress_bar=False,
    )
    sim = torch.matmul(t_emb, p_emb.T).cpu().numpy()
    # Maximize similarity = minimize negative
    row_ind, col_ind = linear_sum_assignment(-sim)
    paired_targets = set(int(i) for i in row_ind)
    paired_preds = set(int(j) for j in col_ind)
    pairs: List[Tuple[int | None, int | None]] = []
    for i, j in zip(row_ind, col_ind):
        pairs.append((int(i), int(j)))
    for i in range(len(targets)):
        if i not in paired_targets:
            pairs.append((i, None))
    for j in range(len(predicted)):
        if j not in paired_preds:
            pairs.append((None, j))
    return pairs


def align_n1_pairs(
    dataset_texts: List[str],
    predicted_texts: List[str],
) -> List[Tuple[int | None, int | None]]:
    return align_lists(dataset_texts, predicted_texts)
