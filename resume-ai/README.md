# ResumeAI - AI简历优化工具

面向非IT行业求职者的智能简历分析优化工具。

## 功能特点

- 🎯 **关键词匹配分析** - 自动检测简历与目标行业的关键词匹配度
- 📊 **评分可视化** - 综合评分、ATS格式、内容完整度多维度评估
- 💡 **优化建议** - AI生成针对性优化建议
- 📝 **简历优化** - 一键生成优化后的简历版本
- 📄 **PDF导出** - 导出分析报告PDF
- 🌐 **双语支持** - 中文/英文简历分析
- 🔐 **用户认证** - 邮箱验证码注册登录
- 📱 **移动端适配** - 完全响应式设计

## 技术栈

- **前端**: HTML/CSS/JavaScript（纯静态）
- **后端**: FastAPI + SQLite
- **AI**: 阿里云DashScope（通义千问）
- **PDF**: ReportLab

## 本地开发

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端运行在 `http://localhost:8001`

### 前端访问

直接打开 `frontend/index.html` 或使用静态服务器：

```bash
cd frontend
python3 -m http.server 5236
```

访问 `http://localhost:5236`

## 部署

详见 [docs/deployment_guide.md](docs/deployment_guide.md)

- **前端**: Vercel静态部署
- **后端**: Vercel Serverless或独立服务器
- **数据库**: Supabase PostgreSQL

## API文档

后端API文档访问: `http://localhost:8001/docs`

## 约束

- 免费用户每日使用5次
- JWT有效期7天
- IP速率限制：每分钟20次请求

## 版本

- v2.0.0 - 2026-05-12
  - 新增PDF导出
  - 新增语言选择
  - 新增密码强度检查
  - 新增IP速率限制

## License

MIT License