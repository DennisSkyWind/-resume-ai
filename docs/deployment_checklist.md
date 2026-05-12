# ResumeAI 部署检查清单

## 部署前检查

### 1. 环境准备
- [ ] 已创建Supabase账号
- [ ] 已创建Supabase项目（区域：Singapore或Tokyo）
- [ ] 已获取SUPABASE_URL和SUPABASE_KEY
- [ ] 已创建Vercel账号
- [ ] 已安装Vercel CLI: `npm i -g vercel`

### 2. 数据库配置
- [ ] 在Supabase SQL Editor执行建表脚本
- [ ] users表创建成功
- [ ] resumes表创建成功
- [ ] usage表创建成功
- [ ] verification_codes表创建成功

### 3. 环境变量配置
- [ ] 创建.env文件
- [ ] 配置SUPABASE_URL
- [ ] 配置SUPABASE_KEY
- [ ] 配置JWT_SECRET（至少32字符）
- [ ] 配置DASHSCOPE_API_KEY

### 4. 后端配置
- [ ] 安装依赖: pip install -r requirements.txt
- [ ] 本地测试通过: python main.py
- [ ] API健康检查: /health 返回正常
- [ ] mangum已安装（Vercel部署）

### 5. 前端配置
- [ ] 确认API地址配置正确
- [ ] 本地打开index.html测试
- [ ] 登录功能正常
- [ ] 分析功能正常

## Vercel部署步骤

### Step 1: 登录Vercel
```bash
vercel login
```

### Step 2: 部署项目
```bash
cd resume-ai
vercel
```

### Step 3: 配置环境变量
在Vercel Dashboard → Settings → Environment Variables添加：
- JWT_SECRET
- DASHSCOPE_API_KEY
- SUPABASE_URL (可选)
- SUPABASE_KEY (可选)

### Step 4: 验证部署
- [ ] 访问部署URL
- [ ] 前端页面正常加载
- [ ] API /health正常响应
- [ ] 登录功能正常
- [ ] 分析功能正常

## 部署后配置（可选）

### 自定义域名
- [ ] 在Vercel添加自定义域名
- [ ] 配置DNS解析
- [ ] SSL证书自动配置

### 监控
- [ ] Vercel Analytics启用
- [ ] 错误日志监控

## 常见问题

### Q: API返回500错误
A: 检查环境变量是否正确配置

### Q: PDF导出失败
A: 确认reportlab依赖已安装，字体路径正确

### Q: 验证码发送失败
A: 检查EMAIL_SMTP配置，或使用Supabase Auth

## 部署完成确认

- [ ] 所有功能测试通过
- [ ] 用户注册登录正常
- [ ] 简历分析正常
- [ ] PDF导出正常
- [ ] 记录生产环境URL