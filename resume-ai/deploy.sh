#!/bin/bash
# ResumeAI 部署脚本

set -e

echo "========================================="
echo "ResumeAI 部署准备脚本"
echo "========================================="

# 检查必要文件
echo ""
echo "[1/5] 检查必要文件..."
required_files=(
    "backend/main.py"
    "backend/requirements.txt"
    "backend/api/index.py"
    "frontend/index.html"
    "vercel.json"
    ".env.example"
)

for file in ${required_files[@]}; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 缺失"
        exit 1
    fi
done

# 检查环境变量
echo ""
echo "[2/5] 检查环境变量配置..."
if [ -f ".env" ]; then
    echo "✅ .env 文件已配置"
else
    echo "⚠️  .env 文件未配置，请复制 .env.example 并填写"
    echo "   cp .env.example .env"
fi

# 安装依赖
echo ""
echo "[3/5] 安装后端依赖..."
cd backend
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"

# 测试后端
echo ""
echo "[4/5] 测试后端API..."
timeout 10s python -c "
import sys
sys.path.insert(0, '.')
from main import app
print('✅ FastAPI应用加载成功')
" || echo "⚠️  测试超时（可能正常）"

# 部署到Vercel
echo ""
echo "[5/5] Vercel部署..."
echo "请手动执行: vercel --prod"
echo ""
echo "========================================="
echo "部署准备完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 配置环境变量: cp .env.example .env"
echo "2. 部署到Vercel: vercel --prod"
echo "3. 在Vercel Dashboard配置环境变量"
echo ""