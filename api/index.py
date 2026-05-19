# Vercel Serverless 入口文件
import sys
import os
import traceback
import json

# 设置环境
os.environ["VERCEL"] = "1"

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def handler(event, context):
    # 打印请求信息
    print(f"Event: {json.dumps(event, default=str)[:500]}")
    
    try:
        # 动态导入main
        from main import app
        from mangum import Mangum
        
        # 创建Mangum适配器
        mangum_handler = Mangum(app, lifespan="off")
        result = mangum_handler(event, context)
        
        print(f"Result: {json.dumps(result, default=str)[:500]}")
        return result
    except Exception as e:
        error_msg = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_msg)  # 输出到Vercel日志
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "traceback": traceback.format_exc()}),
            "headers": {"Content-Type": "application/json"}
        }