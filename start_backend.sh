#!/bin/bash
# ResumeAI 启动脚本

cd /home/ubuntu/.openclaw/workspace/resume-ai/backend

echo "启动 ResumeAI 后端服务..."
echo "端口: 8001"
echo "访问: http://192.168.2.16:8001"

python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload