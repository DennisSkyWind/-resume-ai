# Vercel Serverless 入口文件
# 用于将FastAPI适配到Vercel Functions

import sys
import os

# 当前目录就是api目录，直接导入main
from main import app
from mangum import Mangum

# Vercel handler
handler = Mangum(app, lifespan="off")