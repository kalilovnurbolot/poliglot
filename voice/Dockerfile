FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG VOSK_MODEL=vosk-model-small-ru-0.22

RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 curl unzip \
    && curl -fsSL -o /tmp/model.zip https://alphacephei.com/vosk/models/${VOSK_MODEL}.zip \
    && unzip -q /tmp/model.zip -d /models \
    && mv /models/${VOSK_MODEL} /models/ru \
    && rm /tmp/model.zip \
    && apt-get purge -y curl unzip && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 2700

CMD ["python", "server.py"]
