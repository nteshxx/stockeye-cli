FROM python:3.13-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY stockeye/ stockeye/

RUN pip install --upgrade pip setuptools wheel
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends bash && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels

RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

CMD ["stockeye"]
