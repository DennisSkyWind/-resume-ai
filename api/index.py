# Vercel Serverless 入口文件
import sys
import os
import traceback
import json

# 设置环境
os.environ["VERCEL"] = "1"

def handler(event, context):
    try:
        # 动态导入main
        from main import app
        from mangum import Mangum
        
        # 创建Mangum适配器
        mangum_handler = Mangum(app, lifespan="off")
        return mangum_handler(event, context)
    except Exception as e:
        error_msg = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_msg)  # 输出到Vercel日志
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "traceback": traceback.format_exc()}),
            "headers": {"Content-Type": "application/json"}
        }