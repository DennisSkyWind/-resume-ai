# ResumeAI 云端部署执行计划

## 部署方案选择

**推荐方案**: Vercel + Supabase（免费MVP）

| 方案 | 成本 | 适用场景 |
|------|------|----------|
| Vercel | 免费 | MVP测试、快速上线 |
| Render | 免费 | 小规模运营 |
| Docker | 自托管 | 生产环境 |

---

## Phase 1: GitHub仓库准备 (预计15分钟)

### 任务清单
- [ ] 在GitHub创建公开仓库 `resume-ai`
- [ ] 配置Git远程仓库
- [ ] 推送代码到GitHub
- [ ] 验证仓库可见

### 执行步骤

```bash
# 1. 在GitHub创建仓库（浏览器操作）
# https://github.com/new
# Repository name: resume-ai
# Public

# 2. 配置远程仓库
git remote add origin https://github.com/你的用户名/resume-ai.git

# 3. 推送代码
git push -u origin master
```

---

## Phase 2: Vercel部署 (预计20分钟)

### 任务清单
- [ ] 登录Vercel（GitHub账号）
- [ ] 导入GitHub仓库
- [ ] 配置项目设置
- [ ] 配置环境变量
- [ ] 执行部署
- [ ] 验证部署成功

### 执行步骤

```bash
# 1. 登录Vercel
# https://vercel.com → Continue with GitHub

# 2. 导入项目
# Add New → Project → 选择 resume-ai

# 3. 配置环境变量（在Vercel Dashboard）
JWT_SECRET=resumeai_jwt_secret_key_2026_prod
DASHSCOPE_API_KEY=sk-sp-e8d1076e8dd4461d8d1edf2542f8de68

# 4. 点击 Deploy
```

---

## Phase 3: Supabase数据库 (预计30分钟，可选)

### 说明
- 当前使用SQLite本地数据库
- MVP阶段可以继续使用SQLite
- Supabase用于生产环境（多用户、持久化）

### 任务清单
- [ ] 创建Supabase项目
- [ ] 执行建表SQL
- [ ] 配置环境变量
- [ ] 测试数据库连接

### 执行步骤

```bash
# 1. 创建Supabase项目
# https://supabase.com → New Project

# 2. 执行建表SQL（参考 docs/supabase_setup.md）

# 3. 配置环境变量
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
```

---

## Phase 4: 域名配置 (预计15分钟，可选)

### 任务清单
- [ ] 添加自定义域名
- [ ] 配置DNS解析
- [ ] SSL证书自动配置

---

## 部署时间估算

| Phase | 时间 | 必需 |
|-------|------|------|
| Phase 1: GitHub | 15分钟 | ✅ 必需 |
| Phase 2: Vercel | 20分钟 | ✅ 必需 |
| Phase 3: Supabase | 30分钟 | ⬜ 可选 |
| Phase 4: 域名 | 15分钟 | ⬜ 可选 |

**总计**: 35-80分钟

---

## 下一步行动

**立即执行**: Phase 1 - GitHub仓库准备

请告诉我你的GitHub用户名，我开始推送代码。