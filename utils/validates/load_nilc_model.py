from gensim.models import KeyedVectors


def load_nilc_model() -> KeyedVectors | None:
    try:
        from huggingface_hub import hf_hub_download
        from safetensors.numpy import load_file
    except ImportError:
        print("Dependencias do Hugging Face nao instaladas. Rode pip install -r requirements.txt.")
        return None

    try:
        path = hf_hub_download(
            repo_id="nilc-nlp/fasttext-cbow-300d",
            filename="embeddings.safetensors",
        )
        vocab_path = hf_hub_download(
            repo_id="nilc-nlp/fasttext-cbow-300d",
            filename="vocab.txt",
        )
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
        model = KeyedVectors(vector_size=vectors.shape[1])
        model.add_vectors(vocab, vectors)
        model.fill_norms()
        return model
    except Exception as exc:
        print(f"Falha ao baixar NILC: {exc}")
        return None
