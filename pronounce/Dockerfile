FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PRONOUNCE_MODEL=facebook/wav2vec2-lv-60-espeak-cv-ft

# espeak-ng gives the dictionary pronunciation of words to compare with.
RUN apt-get update \
    && apt-get install -y --no-install-recommends espeak-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-only torch: the server has no GPU, and this build is several times smaller.
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The model is downloaded at build time, so the service starts without the internet.
RUN python -c "import os; from transformers import AutoProcessor, AutoModelForCTC; n = os.environ['PRONOUNCE_MODEL']; AutoProcessor.from_pretrained(n); AutoModelForCTC.from_pretrained(n)"
ENV HF_HUB_OFFLINE=1

COPY phones.py server.py ./

EXPOSE 8030

CMD ["python", "server.py"]
