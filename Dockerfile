FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OLLAMA_HOST=http://host.docker.internal:11434

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.lock* ./
RUN pip install --upgrade pip && \
    if [ -f requirements.lock ]; then \
        pip install -r requirements.lock; \
    else \
        pip install -r requirements.txt; \
    fi

RUN python -c "import nltk; nltk.download('punkt_tab', quiet=True); nltk.download('punkt', quiet=True)"

COPY . .

CMD ["python", "main.py"]
