# ResumeAI 部署指南

## 架构概述

- **前端**: Vercel静态部署
- **后端**: Vercel Serverless Functions 或独立服务器
- **数据库**: Supabase PostgreSQL
- **AI**: 阿里云DashScope API

## 部署步骤

### Step 1: Supabase数据库配置

1. 创建Supabase项目
2. 运行SQL建表脚本（参考 `docs/supabase_setup.md`）
3. 配置环境变量

### Step 2: 后端部署

#### 方式A: Vercel Serverless（推荐）

1. 修改后端为FastAPI适配Vercel:
```python
# backend/api/index.py
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)
```

2. 创建 `vercel.json`:
```json
{
  "functions": "backend/api/**/*.py",
  "routes": [
    {"src": "/api/(.*)", "dest": "/backend/api/index.py"}
  ]
}
```

#### 方式B: 独立服务器

使用Supervisor + Nginx部署FastAPI服务。

### Step 3: 前端部署

1. 修改API地址为生产环境URL
2. Vercel部署:
```bash
cd frontend
vercel --prod
```

### Step 4: 环境变量配置

在Vercel Dashboard设置环境变量:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `JWT_SECRET`
- `DASHSCOPE_API_KEY`

## 检查清单

- [ ] Supabase数据库表创建完成
- [ ] 后端API部署成功
- [ ] 前端静态部署成功
- [ ] 环境变量配置完成
- [ ] 测试API连通性
- [ ] 测试用户注册登录流程

## 常见问题

### Q: Vercel部署超时?
A: 检查依赖大小，尽量减少不必要的库

### Q: Supabase连接失败?
A: 检查环境变量是否正确配置

### Q: API响应慢?
A: 检查DashScope API调用延迟，考虑增加缓存

## 预估成本

- Supabase免费版: 0元/月（500MB数据库）
- Vercel免费版: 0元/月（100GB带宽）
- DashScope API: 按使用量计费

**总计**: 约0-50元/月（初期）