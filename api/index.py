# Vercel Serverless 入口文件
import sys
import os
import traceback

# 错误处理包装器
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
        return {
            "statusCode": 500,
            "body": error_msg,
            "headers": {"Content-Type": "text/plain"}
        }