#!/usr/bin/env python3
"""初始化管理员账号 - Render启动时自动执行"""

import sqlite3
import hashlib
import os
from datetime import datetime

def get_data_dir():
    if os.environ.get("VERCEL") == "1":
        return "/tmp"
    paths = [
        os.path.join(os.path.dirname(__file__), "data"),
        os.path.join(os.path.dirname(__file__), "..", "data"),
        "/tmp"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except:
            continue
    return "/tmp"

def init_admin():
    """初始化管理员账号"""
    DATA_DIR = get_data_dir()
    DB_PATH = os.path.join(DATA_DIR, "users.db")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 添加缺失字段
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        print("添加is_admin字段")
    
    if 'is_paid' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_paid INTEGER DEFAULT 0")
        print("添加is_paid字段")
    
    conn.commit()
    
    # 创建管理员
    password_hash = hashlib.sha256('Hiller'.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE email = 'zhwffy@hotmail.com'")
    
    if cursor.fetchone():
        cursor.execute("UPDATE users SET is_admin = 1, is_paid = 1 WHERE email = 'zhwffy@hotmail.com'")
        print("已设置管理员权限")
    else:
        cursor.execute('''INSERT INTO users 
            (email, name, password_hash, is_admin, is_paid, created_at)
            VALUES (?, ?, ?, 1, 1, ?)''',
            ('zhwffy@hotmail.com', 'Admin', password_hash, datetime.now().isoformat()))
        print("创建管理员账号: zhwffy@hotmail.com / Hiller")
    
    conn.commit()
    conn.close()
    print("管理员初始化完成")

if __name__ == "__main__":
    init_admin()