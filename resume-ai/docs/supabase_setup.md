# Supabase 部署配置指南

## 1. 创建Supabase项目

1. 访问 https://supabase.com 创建账号
2. 创建新项目，选择区域（推荐：Singapore或Tokyo）
3. 记录以下信息：
   - Project URL: `https://xxxxx.supabase.co`
   - Anon Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`
   - Service Role Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6...`

## 2. 数据库表结构

### users表
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    is_paid BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

### resumes表
```sql
CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    industry VARCHAR(50),
    score INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### usage表
```sql
CREATE TABLE usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50),
    industry VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### verification_codes表
```sql
CREATE TABLE verification_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    code VARCHAR(10),
    used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 3. 环境变量配置

创建 `.env` 文件：
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRE_HOURS=168
DASHSCOPE_API_KEY=your_dashscope_key
```

## 4. 后端代码修改

需要修改 `backend/main.py`：
1. 替换SQLite为Supabase PostgreSQL连接
2. 使用 `supabase` Python客户端库
3. 认证逻辑改用Supabase Auth或保留自定义JWT

## 5. 安装依赖

```bash
pip install supabase
```

## 6. 测试连接

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
result = supabase.table('users').select('*').execute()
print(result.data)
```