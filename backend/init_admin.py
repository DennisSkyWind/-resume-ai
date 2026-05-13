#!/usr/bin/env python3
"""初始化管理员账号 - Render启动时自动执行"""

import sqlite3
import hashlib
import os
from datetime import datetime

def init_admin(USER_DB_PATH=None):
    """初始化管理员账号"""
    
    # 如果没有传入路径，使用默认计算
    if USER_DB_PATH is None:
        DATA_DIR = get_data_dir()
        USER_DB_PATH = os.path.join(DATA_DIR, "users.db")
    
    print(f"[init_admin] 使用数据库: {USER_DB_PATH}")
    
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 添加缺失字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            print("[init_admin] 添加is_admin字段")
        
        if 'is_paid' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_paid INTEGER DEFAULT 0")
            print("[init_admin] 添加is_paid字段")
        
        conn.commit()
        
        # 创建管理员
        password_hash = hashlib.sha256('Hiller'.encode()).hexdigest()
        cursor.execute("SELECT id FROM users WHERE email = 'zhwffy@hotmail.com'")
        
        if cursor.fetchone():
            cursor.execute("UPDATE users SET is_admin = 1, is_paid = 1 WHERE email = 'zhwffy@hotmail.com'")
            print("[init_admin] 已设置管理员权限")
        else:
            cursor.execute('''INSERT INTO users 
                (email, name, password_hash, is_admin, is_paid, created_at)
                VALUES (?, ?, ?, 1, 1, ?)''',
                ('zhwffy@hotmail.com', 'Admin', password_hash, datetime.now().isoformat()))
            print("[init_admin] 创建管理员账号: zhwffy@hotmail.com / Hiller")
        
        conn.commit()
        conn.close()
        print("[init_admin] 管理员初始化完成")
        return True
    except Exception as e:
        print(f"[init_admin] 错误: {e}")
        return False

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

if __name__ == "__main__":
    init_admin()