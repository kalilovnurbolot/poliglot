FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MEANING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
    MEANING_CACHE_DIR=/models

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The model is downloaded at build time, so the service starts without the internet.
RUN python -c "import os; from fastembed import TextEmbedding; TextEmbedding(os.environ['MEANING_MODEL'], cache_dir=os.environ['MEANING_CACHE_DIR'])"

# Use only the downloaded copy, never check the hub at start.
ENV HF_HUB_OFFLINE=1

COPY server.py .

EXPOSE 8020

CMD ["python", "server.py"]
