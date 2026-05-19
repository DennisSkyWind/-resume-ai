# 最简单的Vercel测试API
def handler(event, context):
    return {
        "statusCode": 200,
        "body": '{"success": true, "message": "Test OK"}',
        "headers": {"Content-Type": "application/json"}
    }