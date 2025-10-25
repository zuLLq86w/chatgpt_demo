# ---------- 基础镜像 ----------
FROM python:3.12-slim


# 安装依赖工具和 uv
RUN apt-get update && apt-get install -y \
    curl build-essential libffi-dev git ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv

# ---------- 工作目录 ----------
WORKDIR /app

# 拷贝依赖文件并安装（无虚拟环境）
COPY pyproject.toml .
RUN uv sync
# ---------- 复制项目 ----------
COPY . .

# 激活虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# ---------- 启动命令 ----------
CMD ["python", "main.py"]

