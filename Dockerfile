# ---------- 构建阶段 ----------
FROM python:3.12-slim AS builder

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y build-essential curl && pip install uv && \
    uv sync --no-dev

# ---------- 运行阶段 ----------
FROM python:3.12-slim
WORKDIR /app

COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["python", "main.py"]
