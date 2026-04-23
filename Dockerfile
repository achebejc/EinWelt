# ── builder stage ────────────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

# Install build-time deps needed to compile any C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ── runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

# libpq5 is the shared library psycopg2-binary links against at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the builder
COPY --from=builder /install /usr/local

WORKDIR /app

COPY app/ ./app/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
