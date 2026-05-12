# Simple test handler for Vercel

def handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello from Vercel!",
        "headers": {"Content-Type": "text/plain"}
    }