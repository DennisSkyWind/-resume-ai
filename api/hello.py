# Vercel 最小测试API
import json

def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"success": True, "message": "Hello from Vercel!", "event": str(event)[:200]}),
        "headers": {"Content-Type": "application/json"}
    }