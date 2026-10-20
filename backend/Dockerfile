# Styles are built here from the templates, so a rebuild picks up new Tailwind classes
# without Node on the host (apps/web/tailwind/input.css).
FROM node:22-alpine AS css

WORKDIR /build
RUN npm install --no-save --no-audit --no-fund tailwindcss@4.3.3 @tailwindcss/cli@4.3.3
COPY apps/web apps/web
RUN npx tailwindcss -i apps/web/tailwind/input.css -o app.css --minify


FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=css /build/app.css apps/web/static/web/css/app.css

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
