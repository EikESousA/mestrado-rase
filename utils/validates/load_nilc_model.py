from typing import Dict, Iterable, Set

from gensim.models import KeyedVectors


_NILC_REPOS: Dict[str, str] = {
    "fasttext": "nilc-nlp/fasttext-cbow-300d",
    "word2vec": "nilc-nlp/word2vec-cbow-300d",
}


def load_nilc_embeddings(
    variant: str = "fasttext",
    vocab_whitelist: Iterable[str] | None = None,
) -> KeyedVectors | None:
    repo_id = _NILC_REPOS.get(variant)
    if repo_id is None:
        print(f"Variante NILC desconhecida: {variant}")
        return None

    try:
        from huggingface_hub import hf_hub_download
        from safetensors.numpy import load_file
    except ImportError:
        print("Dependencias do Hugging Face nao instaladas. Rode pip install -r requirements.txt.")
        return None

    try:
        path = hf_hub_download(repo_id=repo_id, filename="embeddings.safetensors")
        vocab_path = hf_hub_download(repo_id=repo_id, filename="vocab.txt")
        data = load_file(path)
        vectors = data["embeddings"]
        with open(vocab_path, "r", encoding="utf-8") as file:
            vocab = [word.strip() for word in file if word.strip()]
        if vocab and vocab[0].isdigit():
            vocab = vocab[1:]
        if len(vocab) != vectors.shape[0]:
            min_len = min(len(vocab), vectors.shape[0])
            vocab = vocab[:min_len]
            vectors = vectors[:min_len]

        if vocab_whitelist is not None:
            whitelist: Set[str] = {w.lower() for w in vocab_whitelist if w}
            kept_indices = [
                i for i, w in enumerate(vocab) if w.lower() in whitelist
            ]
            if kept_indices:
                vocab = [vocab[i] for i in kept_indices]
                vectors = vectors[kept_indices]

        model = KeyedVectors(vector_size=vectors.shape[1])
        model.add_vectors(vocab, vectors)
        model.fill_norms()
        return model
    except Exception as exc:
        print(f"Falha ao baixar NILC ({variant}): {exc}")
        return None


def load_nilc_model(vocab_whitelist: Iterable[str] | None = None) -> KeyedVectors | None:
    return load_nilc_embeddings("word2vec", vocab_whitelist=vocab_whitelist)


def load_pt_fasttext(vocab_whitelist: Iterable[str] | None = None) -> KeyedVectors | None:
    return load_nilc_embeddings("fasttext", vocab_whitelist=vocab_whitelist)
