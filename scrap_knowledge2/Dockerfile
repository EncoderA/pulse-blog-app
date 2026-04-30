FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (kept minimal; many python deps ship wheels)
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md /app/
COPY src/ /app/src/

RUN python -m pip install --upgrade pip setuptools wheel \
  && python -m pip install -e ".[embeddings]"

EXPOSE 8000

CMD ["blog-kb", "serve", "--host", "0.0.0.0", "--port", "8000"]