FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# <language code>=<Vosk model>: the server loads /models/<code> for each of them.
ARG VOSK_MODELS="ru=vosk-model-small-ru-0.22 en=vosk-model-small-en-us-0.15 de=vosk-model-small-de-0.15"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 curl unzip \
    && mkdir -p /models \
    && for pair in ${VOSK_MODELS}; do \
         code=${pair%%=*}; model=${pair#*=}; \
         curl -fsSL -o /tmp/model.zip https://alphacephei.com/vosk/models/${model}.zip \
         && unzip -q /tmp/model.zip -d /models \
         && mv /models/${model} /models/${code} \
         && rm /tmp/model.zip || exit 1; \
       done \
    && apt-get purge -y curl unzip && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV VOICE_LANGUAGES=ru,en,de

EXPOSE 2700

CMD ["python", "server.py"]
