FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -e .

# 创建上传目录
RUN mkdir -p /app/static/uploads-2

EXPOSE 7860

CMD ["image-hosting"] 