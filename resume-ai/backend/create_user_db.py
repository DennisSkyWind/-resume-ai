#!/usr/bin/env python3
"""创建ResumeAI用户数据库"""

import sqlite3
import os

DB_PATH = '/home/ubuntu/.openclaw/workspace/resume-ai/data/users.db'

# 创建数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_paid BOOLEAN DEFAULT FALSE,
    plan_type TEXT DEFAULT 'free'
)
''')

# 用户简历表
cursor.execute('''
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT,
    content TEXT,
    industry TEXT,
    score INTEGER,
    optimized_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# 使用记录表
cursor.execute('''
CREATE TABLE IF NOT EXISTS usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    industry TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# 创建索引
cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_resumes_user ON resumes(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_user ON usage(user_id)')

conn.commit()
conn.close()

print(f'✅ 用户数据库已创建: {DB_PATH}')
print('表结构:')
print('  - users: 用户表')
print('  - resumes: 简历表')
print('  - usage: 使用记录表')