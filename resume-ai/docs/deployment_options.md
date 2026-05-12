# ResumeAI 部署方案

提供多种部署方式，按需选择：

## 方案对比

| 方案 | 成本 | 优点 | 缺点 | 推荐场景 |
|------|------|------|------|----------|
| Vercel | 免费 | 部署简单、CDN加速 | Serverless限制 | MVP测试 |
| Render | 免费 | 持续运行、无限制 | 冷启动慢 | 小规模运营 |
| Docker | 自托管 | 完全控制、无限制 | 需服务器 | 生产环境 |
| 本地 | 免费 | 快速测试 | 仅开发用 | 开发调试 |

---

## 方案1: Vercel部署（推荐）

### 步骤

1. **安装Vercel CLI**
```bash
npm i -g vercel
```

2. **登录Vercel**
```bash
vercel login
```

3. **部署项目**
```bash
cd resume-ai
vercel --prod
```

4. **配置环境变量**
   在Vercel Dashboard → Settings → Environment Variables添加：
   - `JWT_SECRET`
   - `DASHSCOPE_API_KEY`

### Supabase数据库配置（可选）

如果使用Supabase作为数据库：
1. 创建Supabase项目
2. 运行建表SQL（见 docs/supabase_setup.md）
3. 添加环境变量：
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

---

## 方案2: Render部署

### 步骤

1. **连接GitHub仓库**
   - 登录 render.com
   - 连接GitHub账号
   - 选择 resume-ai 仓库

2. **自动部署**
   - render.yaml 会自动配置两个服务：
     - `resume-ai-api` (后端)
     - `resume-ai-frontend` (前端)

3. **配置环境变量**
   在Render Dashboard添加：
   - `DASHSCOPE_API_KEY`
   - `JWT_SECRET` (自动生成)

### 服务地址

- 前端: https://resume-ai-frontend.onrender.com
- 后端: https://resume-ai-api.onrender.com

---

## 方案3: Docker部署

### 本地测试

```bash
docker-compose up -d
```

访问：
- 前端: http://localhost:5236
- 后端: http://localhost:8001

### 服务器部署

1. **构建镜像**
```bash
docker build -t resume-ai .
```

2. **运行容器**
```bash
docker run -d \
  -p 8001:8001 \
  -e JWT_SECRET=your_secret \
  -e DASHSCOPE_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  resume-ai
```

---

## 方案4: 本地开发

### 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 启动前端

```bash
cd frontend
python3 -m http.server 5236
```

---

## 环境变量说明

| 变量 | 必需 | 说明 |
|------|------|------|
| `JWT_SECRET` | ✅ | JWT密钥，至少16字符 |
| `DASHSCOPE_API_KEY` | ✅ | 阿里云AI API密钥 |
| `JWT_EXPIRE_HOURS` | ⬜ | Token有效期，默认168小时 |
| `FREE_LIMIT` | ⬜ | 每日免费次数，默认5次 |
| `SUPABASE_URL` | ⬜ | Supabase项目URL |
| `SUPABASE_KEY` | ⬜ | Supabase密钥 |

---

## 部署后验证

1. **健康检查**
```bash
curl https://your-domain/api/v1/health
```

2. **注册测试**
   - 打开前端页面
   - 测试邮箱验证码注册

3. **功能测试**
   - 登录
   - 简历分析
   - PDF导出

---

## 常见问题

### Vercel部署超时
- 检查requirements.txt依赖大小
- 删除不必要的依赖

### Render冷启动慢
- 正常现象，首次访问需等待
- 可设置健康检查保活

### Docker容器启动失败
- 检查端口冲突
- 确认环境变量配置

---

## 推荐部署流程

```
1. 本地测试 ✅ → 2. Vercel部署 ✅ → 3. 用户测试 ✅ → 4. Render/Docker生产部署
```