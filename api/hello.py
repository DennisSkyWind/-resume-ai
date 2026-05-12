# Minimal Vercel Python function test

def handler(event, context):
    return {
        "statusCode": 200,
        "body": '{"message": "Hello from ResumeAI!"}',
        "headers": {
            "Content-Type": "application/json"
        }
    }