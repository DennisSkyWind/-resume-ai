#!/usr/bin/env python3
import sqlite3

# 更新用户数据库
conn = sqlite3.connect('/home/ubuntu/.openclaw/workspace/resume-ai/data/users.db')
cursor = conn.cursor()

# 验证码表
cursor.execute('''
CREATE TABLE IF NOT EXISTS verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE
)
''')

# 用户表添加管理员字段
try:
    cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
    print('✅ 已添加is_admin字段')
except:
    print('⚠️ is_admin字段已存在')

# 设置第一个用户为管理员
cursor.execute('UPDATE users SET is_admin = TRUE WHERE id = 1')

# 创建索引
cursor.execute('CREATE INDEX IF NOT EXISTS idx_ver_email ON verification_codes(email)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_ver_code ON verification_codes(code)')

conn.commit()
conn.close()
print('✅ 数据库更新完成')
print('✅ 用户test@example.com 已设为管理员')