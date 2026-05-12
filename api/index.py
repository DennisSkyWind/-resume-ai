# Vercel Serverless 入口文件
# 用于将FastAPI适配到Vercel Functions

import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from mangum import Mangum
from main import app

# Vercel handler
handler = Mangum(app, lifespan="off")