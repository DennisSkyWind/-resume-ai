FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制数据目录
COPY data/ ./data/

# 创建日志目录
RUN mkdir -p data

# 环境变量
ENV PORT=8001
ENV JWT_EXPIRE_HOURS=168
ENV FREE_LIMIT=5

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]