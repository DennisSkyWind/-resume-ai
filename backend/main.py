"""
ResumeAI Backend - FastAPIwith User Authentication
简历优化系统后端服务（带用户认证）
"""

from fastapi import FastAPI, HTTPException, Depends, Header, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import re
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
import random
import tempfile
import logging

# 配置日志 - Vercel兼容（无文件日志）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入邮箱发送模块
from email_sender import send_verification_code, generate_code, get_email_config, EMAIL_CONFIG

# 文件解析模块
import pdfplumber
from docx import Document

# PDF生成模块
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

# 初始化FastAPI
app = FastAPI(
    title="ResumeAI API",
    description="AI简历优化系统 - 为非IT行业求职者提供简历优化服务",
    version="2.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据目录 - 多环境兼容
# Render: 使用backend目录下的data子目录
# Vercel: 使用/tmp目录（Serverless）
# 本地: 使用项目根目录的data目录
def get_data_dir():
    # 检查环境变量
    if os.environ.get("VERCEL") == "1":
        return "/tmp"
    
    # Render或本地环境
    # 尝试多个可能的路径
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "data"),  # backend/data
        os.path.join(os.path.dirname(__file__), "..", "data"),  # project_root/data
        "/tmp"  # fallback
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
        # 尝试创建目录
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except:
            continue
    
    return "/tmp"

DATA_DIR = get_data_dir()
USER_DB_PATH = os.path.join(DATA_DIR, "users.db")

# 确保数据库和所有表存在（每次启动都检查）
def ensure_tables_exist():
    """确保所有必要的表都存在"""
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 创建所有表（IF NOT EXISTS确保不会重复创建）
    conn.execute('''CREATE TABLE IF NOT EXISTS users
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password_hash TEXT,
        name TEXT,
        verified INTEGER DEFAULT 0,
        daily_limit INTEGER DEFAULT 5,
        last_reset TEXT,
        last_login TEXT,
        is_admin INTEGER DEFAULT 0,
        is_paid INTEGER DEFAULT 0,
        created_at TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS verification_codes
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        code TEXT,
        expires_at TEXT,
        used INTEGER DEFAULT 0,
        created_at TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS user_templates
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        template_id TEXT,
        custom_settings TEXT,
        is_default INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS usage
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        industry TEXT,
        created_at TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS orders
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_id TEXT,
        amount REAL,
        status TEXT,
        created_at TEXT)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS resumes
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        industry TEXT,
        score REAL,
        created_at TEXT)''')
    
    conn.commit()
    
    # 确保字段存在（ALTER TABLE）
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'is_admin' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    if 'is_paid' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_paid INTEGER DEFAULT 0")
    
    conn.commit()
    
    # 初始化管理员账号
    cursor.execute("SELECT * FROM users WHERE email = ?", ('zhwffy@hotmail.com',))
    admin = cursor.fetchone()
    
    if not admin:
        # 创建管理员
        admin_password = "Hiller"
        admin_hash = hashlib.sha256(admin_password.encode()).hexdigest()
        cursor.execute('''INSERT INTO users 
            (email, password_hash, name, verified, is_admin, is_paid, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            ('zhwffy@hotmail.com', admin_hash, 'Admin', 1, 1, 1, datetime.now().isoformat()))
        conn.commit()
        logger.info("Admin account created: zhwffy@hotmail.com")
    
    conn.close()
    logger.info("Database tables verified and ready")

# 启动时确保表存在
ensure_tables_exist()

# JWT配置（使用固定密钥）
JWT_SECRET = "resumeai_jwt_secret_key_2026"  # 固定密钥，生产环境应使用环境变量
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 168  # 7天有效期

# 免费用户限制
FREE_LIMIT = 5  # 每天免费使用次数

# IP速率限制配置
RATE_LIMIT_WINDOW = 60  # 60秒窗口
RATE_LIMIT_MAX_REQUESTS = 20  # 每分钟最大请求次数
ip_request_counts = {}  # IP请求计数（内存存储）

def check_rate_limit(ip: str) -> bool:
    """检查IP速率限制"""
    now = datetime.now()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    # 清理过期记录
    if ip in ip_request_counts:
        ip_request_counts[ip] = [t for t in ip_request_counts[ip] if t > window_start]
    else:
        ip_request_counts[ip] = []
    
    # 检查请求次数
    if len(ip_request_counts[ip]) >= RATE_LIMIT_MAX_REQUESTS:
        return False
    
    # 记录本次请求
    ip_request_counts[ip].append(now)
    return True

# PDF中文字体配置
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
try:
    pdfmetrics.registerFont(TTFont('NotoSansCJK', FONT_PATH, subfontIndex=0))
    pdfmetrics.registerFont(TTFont('NotoSansCJK-Bold', FONT_BOLD_PATH, subfontIndex=0))
    PDF_FONT_NAME = 'NotoSansCJK'
    PDF_FONT_BOLD = 'NotoSansCJK-Bold'
except Exception as e:
    print(f"字体注册失败: {e}")
    PDF_FONT_NAME = 'Helvetica'
    PDF_FONT_BOLD = 'Helvetica-Bold'

# 阿里云Coding API配置
DASHSCOPE_API_KEY = "sk-sp-e8d1076e8dd4461d8d1edf2542f8de68"
DASHSCOPE_BASE_URL = "https://coding.dashscope.aliyuncs.com/v1"
DASHSCOPE_MODEL = "qwen3.5-plus"

# 加载关键词库
def load_keywords():
    """加载关键词数据库"""
    # 首先尝试从backend目录加载
    keywords_file = os.path.join(os.path.dirname(__file__), "keywords.json")
    logger.info(f"尝试加载关键词文件: {keywords_file}")
    
    if os.path.exists(keywords_file):
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载关键词数据库，包含 {len(data)} 个行业")
            return data
        except Exception as e:
            logger.error(f"加载关键词文件失败: {e}")
    
    # 兜底：尝试data目录
    keywords_file = os.path.join(DATA_DIR, "keywords.json")
    logger.info(f"尝试从data目录加载: {keywords_file}")
    
    if os.path.exists(keywords_file):
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"从data目录成功加载关键词数据库")
            return data
        except Exception as e:
            logger.error(f"从data目录加载失败: {e}")
    
    logger.warning("关键词数据库未加载，使用空字典")
    return {}

KEYWORDS_DB = load_keywords()
logger.info(f"KEYWORDS_DB 初始化完成，行业数: {len(KEYWORDS_DB)}")

# ========== 用户认证函数 ==========

def get_user_db():
    conn = sqlite3.connect(USER_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_strength(password: str) -> dict:
    """检查密码强度"""
    result = {
        "valid": True,
        "score": 0,
        "message": ""
    }
    
    # 长度检查
    if len(password) < 6:
        result["valid"] = False
        result["message"] = "密码长度至少6位"
        return result
    elif len(password) >= 8:
        result["score"] += 1
    
    # 复杂度检查
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password)
    
    complexity = sum([has_lower, has_upper, has_digit, has_special])
    result["score"] += complexity
    
    # 评分
    if result["score"] >= 4:
        result["message"] = "密码强度：强"
    elif result["score"] >= 2:
        result["message"] = "密码强度：中等"
    else:
        result["message"] = "密码强度：弱，建议包含大小写字母、数字和特殊字符"
    
    return result

def create_token(user_id: int, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def detect_language(text: str) -> str:
    """检测文本语言（中文/英文）"""
    # 统计中文字符比例
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    
    if total_chars == 0:
        return "zh"  # 默认中文
    
    chinese_ratio = chinese_chars / total_chars
    
    # 中文字符占比超过30%视为中文
    if chinese_ratio > 0.3:
        return "zh"
    else:
        return "en"

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证token")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (payload["user_id"],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return dict(user)

def check_usage_limit(user_id: int) -> bool:
    """检查用户今日使用次数"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 检查是否付费用户
    cursor.execute("SELECT is_paid FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user and user["is_paid"]:
        conn.close()
        return True  # 付费用户无限制
    
    # 检查今日使用次数
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usage 
        WHERE user_id = ? AND DATE(created_at) = ?
    """, (user_id, today))
    
    result = cursor.fetchone()
    conn.close()
    
    return result["count"] < FREE_LIMIT

def record_usage(user_id: int, action: str, industry: str = None):
    """记录用户使用"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usage (user_id, action, industry)
        VALUES (?, ?, ?)
    """, (user_id, action, industry))
    conn.commit()
    conn.close()

# ========== 请求模型 ==========

class SendCodeRequest(BaseModel):
    email: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    code: str  # 验证码

class LoginRequest(BaseModel):
    email: str
    password: str

class AnalyzeRequest(BaseModel):
    resume_content: str
    industry: str
    language: str = "zh"
    jd_content: Optional[str] = None

class OptimizeRequest(BaseModel):
    resume_content: str
    industry: str
    language: str = "zh"
    jd_content: Optional[str] = None

# ========== 用户认证API ==========

# 显式处理OPTIONS预检请求（确保CORS正常工作）
@app.options("/api/v1/{path:path}")
async def options_handler():
    return Response(status_code=200)

@app.post("/api/v1/send-code")
async def send_code(request: SendCodeRequest):
    """发送验证码"""
    try:
        import sqlite3
        
        conn = get_user_db()
        cursor = conn.cursor()
        
        # 检查邮箱是否已注册
        cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 生成验证码
        code = generate_code(EMAIL_CONFIG["code_length"])
        expires_at = datetime.now() + timedelta(minutes=EMAIL_CONFIG["code_expire_minutes"])
        
        # 保存验证码到数据库
        cursor.execute("""
            INSERT INTO verification_codes (email, code, expires_at)
            VALUES (?, ?, ?)
        """, (request.email, code, expires_at.isoformat()))
        conn.commit()
        conn.close()
        
        # 发送验证码
        result = send_verification_code(request.email, code)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "test_code": result.get("test_code")  # 测试模式返回验证码
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送验证码失败: {e}")
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")

@app.post("/api/v1/register")
async def register(request: RegisterRequest):
    """用户注册（需要验证码）"""
    logger.info(f"注册请求: email={request.email}")
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 验证邮箱格式
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", request.email):
        logger.warning(f"注册失败: {request.email} - 邮箱格式不正确")
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    
    # 检查密码强度
    strength = check_password_strength(request.password)
    if not strength["valid"]:
        logger.warning(f"注册失败: {request.email} - 密码强度不足")
        raise HTTPException(status_code=400, detail=strength["message"])
    
    # 检查邮箱是否已存在
    cursor.execute("SELECT id FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        logger.warning(f"注册失败: {request.email} - 邮箱已被注册")
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 验证验证码
    cursor.execute("""
        SELECT * FROM verification_codes 
        WHERE email = ? AND code = ? AND used = FALSE AND expires_at > ?
        ORDER BY created_at DESC LIMIT 1
    """, (request.email, request.code, datetime.now().isoformat()))
    
    code_record = cursor.fetchone()
    
    if not code_record:
        conn.close()
        raise HTTPException(status_code=400, detail="验证码无效或已过期")
    
    # 标记验证码已使用
    cursor.execute("UPDATE verification_codes SET used = TRUE WHERE id = ?", (code_record["id"],))
    
    # 创建用户
    password_hash = hash_password(request.password)
    cursor.execute("""
        INSERT INTO users (email, password_hash, name)
        VALUES (?, ?, ?)
    """, (request.email, password_hash, request.name))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 生成token
    token = create_token(user_id, request.email)
    
    return {
        "success": True,
        "data": {
            "user_id": user_id,
            "email": request.email,
            "token": token,
            "token_type": "Bearer"
        }
    }

@app.post("/api/v1/login")
async def login(request: LoginRequest):
    """用户登录"""
    logger.info(f"登录请求: {request.email}")
    conn = get_user_db()
    cursor = conn.cursor()
    
    password_hash = hash_password(request.password)
    cursor.execute("""
            SELECT id, email, name, daily_limit FROM users WHERE email = ? AND password_hash = ?
        """, (request.email, password_hash))
    
    user = cursor.fetchone()
    
    if not user:
        logger.warning(f"登录失败: {request.email} - 邮箱或密码错误")
        conn.close()
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    # 更新登录时间
    cursor.execute("""
        UPDATE users SET last_login = ? WHERE id = ?
    """, (datetime.now().isoformat(), user["id"]))
    conn.commit()
    conn.close()
    
    # 生成token
    token = create_token(user["id"], user["email"])
    
    return {
        "success": True,
        "data": {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "daily_limit": user["daily_limit"],
            "token": token,
            "token_type": "Bearer"
        }
    }

@app.get("/api/v1/me")
async def get_me(user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 获取今日使用次数
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usage 
        WHERE user_id = ? AND DATE(created_at) = ?
    """, (user["id"], today))
    
    usage = cursor.fetchone()
    
    # 获取简历数量
    cursor.execute("SELECT COUNT(*) as count FROM resumes WHERE user_id = ?", (user["id"],))
    resumes = cursor.fetchone()
    conn.close()
    
    return {
        "success": True,
        "data": {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "is_paid": user["is_paid"],
            "plan_type": user["plan_type"],
            "usage_today": usage["count"],
            "usage_limit": FREE_LIMIT if not user["is_paid"] else "unlimited",
            "resumes_count": resumes["count"]
        }
    }

@app.get("/api/v1/usage")
async def get_usage(user: dict = Depends(get_current_user)):
    """获取用户使用次数详情"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 获取今日使用次数
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT COUNT(*) as count FROM usage 
        WHERE user_id = ? AND DATE(created_at) = ?
    """, (user["id"], today))
    
    usage = cursor.fetchone()
    used_today = usage["count"]
    
    # 获取是否付费
    is_paid = user["is_paid"]
    remaining = "unlimited" if is_paid else max(0, FREE_LIMIT - used_today)
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "used_today": used_today,
            "limit": FREE_LIMIT if not is_paid else "unlimited",
            "remaining": remaining,
            "is_paid": is_paid,
            "can_use": is_paid or used_today < FREE_LIMIT
        }
    }

# ========== 简历API（需认证） ==========

@app.post("/api/v1/upload")
async def upload_resume(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """上传简历文件并提取文本（PDF/Word）"""
    
    # 检查文件类型
    filename = file.filename.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.doc')):
        raise HTTPException(status_code=400, detail="只支持PDF和Word文件（.pdf, .docx, .doc）")
    
    # 检查使用限制
    if not check_usage_limit(user["id"]):
        raise HTTPException(status_code=403, detail="今日免费次数已用完")
    
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        text_content = ""
        
        # 解析PDF
        if filename.endswith('.pdf'):
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
        
        # 解析Word
        elif filename.endswith('.docx') or filename.endswith('.doc'):
            doc = Document(tmp_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content += para.text + "\n"
            # 也提取表格内容
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells]
                    if any(row_text):
                        text_content += " | ".join(row_text) + "\n"
        
        # 清理临时文件
        os.unlink(tmp_path)
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="无法从文件中提取文本内容")
        
        # 记录使用
        record_usage(user["id"], "upload", "file")
        
        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "content": text_content.strip(),
                "length": len(text_content.strip())
            }
        }
        
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")

@app.post("/api/v1/analyze")
async def analyze(request: AnalyzeRequest, user: dict = Depends(get_current_user), 
                  client_ip: Optional[str] = Header(None, alias="X-Forwarded-For")):
    """分析简历（需认证）"""
    # IP速率限制
    ip = client_ip or "unknown"
    if not check_rate_limit(ip):
        logger.warning(f"速率限制触发: IP={ip}")
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    
    logger.info(f"简历分析请求: user={user['id']}, industry={request.industry}, ip={ip}")
    
    if request.industry not in KEYWORDS_DB:
        raise HTTPException(status_code=400, detail=f"不支持的行业: {request.industry}")
    
    # 检查使用限制
    if not check_usage_limit(user["id"]):
        raise HTTPException(status_code=403, detail="今日免费次数已用完，请升级付费或明天再试")
    
    # 分析简历
    result = analyze_resume(request.resume_content, request.industry, request.language, request.jd_content)
    
    # 记录使用
    record_usage(user["id"], "analyze", request.industry)
    
    # 保存简历
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (user_id, content, industry, score)
        VALUES (?, ?, ?, ?)
    """, (user["id"], request.resume_content, request.industry, result["overall_score"]))
    conn.commit()
    conn.close()
    
    return {"success": True, "data": result}

@app.post("/api/v1/optimize")
async def optimize(request: OptimizeRequest, user: dict = Depends(get_current_user)):
    """优化简历（需认证）"""
    if request.industry not in KEYWORDS_DB:
        raise HTTPException(status_code=400, detail=f"不支持的行业: {request.industry}")
    
    # 检查使用限制
    if not check_usage_limit(user["id"]):
        raise HTTPException(status_code=403, detail="今日免费次数已用完")
    
    # 优化简历（简化版）
    result = optimize_resume(request.resume_content, request.industry, request.language)
    
    # 记录使用
    record_usage(user["id"], "optimize", request.industry)
    
    return {"success": True, "data": result}

@app.get("/api/v1/resumes")
async def get_resumes(user: dict = Depends(get_current_user)):
    """获取用户简历历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, industry, score, created_at
        FROM resumes WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 20
    """, (user["id"],))
    
    resumes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"success": True, "data": resumes}

@app.get("/api/v1/resumes/history")
async def get_resumes_history(user: dict = Depends(get_current_user)):
    """获取用户简历历史列表（带分页）"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute("SELECT COUNT(*) as total FROM resumes WHERE user_id = ?", (user["id"],))
    total = cursor.fetchone()["total"]
    
    # 获取历史列表（带更多字段）
    cursor.execute("""
        SELECT 
            id,
            title,
            industry,
            score,
            created_at,
            updated_at,
            LENGTH(content) as content_length
        FROM resumes 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 50
    """, (user["id"],))
    
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {
        "success": True,
        "data": {
            "total": total,
            "history": history
        }
    }

@app.get("/api/v1/resumes/{resume_id}")
async def get_resume_detail(resume_id: int, user: dict = Depends(get_current_user)):
    """获取简历详情"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id,
            user_id,
            title,
            industry,
            score,
            content,
            created_at,
            updated_at
        FROM resumes 
        WHERE id = ? AND user_id = ?
    """, (resume_id, user["id"]))
    
    resume = cursor.fetchone()
    conn.close()
    
    if not resume:
        raise HTTPException(status_code=404, detail="简历不存在或无权访问")
    
    return {
        "success": True,
        "data": dict(resume)
    }

@app.post("/api/v1/export/pdf")
async def export_pdf(user: dict = Depends(get_current_user)):
    """导出简历分析报告PDF"""
    # 生成PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    # 样式配置
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        fontName=PDF_FONT_BOLD,
        fontSize=18,
        spaceAfter=20,
        alignment=1  # 居中
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        fontName=PDF_FONT_BOLD,
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'CustomBody',
        fontName=PDF_FONT_NAME,
        fontSize=12,
        spaceBefore=6,
        spaceAfter=6,
        leading=18
    )
    
    # 构建PDF内容
    elements = []
    
    # 标题
    elements.append(Paragraph("简历分析报告", title_style))
    elements.append(Spacer(1, 20))
    
    # 基本信息
    elements.append(Paragraph("基本信息", heading_style))
    info_data = [
        ["分析日期", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["用户邮箱", user.get("email", "未知")],
    ]
    info_table = Table(info_data, colWidths=[80*mm, 80*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), PDF_FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 30))
    
    # 落款
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(
        f"{datetime.now().strftime('%Y年%m月%d日')} 智能与数字化中心·数据智能",
        ParagraphStyle('Footer', fontName=PDF_FONT_NAME, fontSize=12, alignment=2)
    ))
    
    # 生成PDF
    doc.build(elements)
    buffer.seek(0)
    
    # 返回PDF响应
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resume_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )

# ========== 核心分析函数 ==========

def analyze_resume(resume: str, industry: str, language: str, jd: Optional[str] = None):
    """分析简历关键词匹配度"""
    
    industry_keywords = KEYWORDS_DB.get(industry, {})
    required_keywords = industry_keywords.get("keywords", {}).get("required", [])
    preferred_keywords = industry_keywords.get("keywords", {}).get("preferred", [])
    
    all_keywords = required_keywords + preferred_keywords
    
    keywords_found = []
    keywords_missing = []
    total_weight = 0
    matched_weight = 0
    
    for kw in all_keywords:
        keyword_text = kw["keyword"] if language == "zh" else kw.get("en", kw["keyword"])
        count = len(re.findall(keyword_text, resume, re.IGNORECASE))
        found = count > 0
        
        if found:
            keywords_found.append({
                "keyword": kw["keyword"],
                "weight": kw["weight"],
                "count": count,
                "found": True
            })
            matched_weight += kw["weight"]
        
        total_weight += kw["weight"]
    
    # 计算缺失关键词
    found_kw_list = [k["keyword"] for k in keywords_found]
    for kw in all_keywords:
        if kw["keyword"] not in found_kw_list:
            keywords_missing.append({
                "keyword": kw["keyword"],
                "weight": kw["weight"],
                "suggestion": f"添加{kw['keyword']}相关经验描述"
            })
    
    # 计算评分
    keyword_score = round(matched_weight / total_weight * 100, 1) if total_weight > 0 else 0
    ats_score = check_ats(resume)
    overall_score = round((keyword_score * 0.6 + ats_score * 0.4), 1)
    
    suggestions = generate_suggestions(resume, keywords_missing, industry)
    
    return {
        "overall_score": overall_score,
        "keyword_score": keyword_score,
        "ats_score": ats_score,
        "keywords_found": keywords_found,
        "keywords_missing": keywords_missing,
        "suggestions": suggestions,
        "industry_name": industry_keywords.get("name", industry)
    }

def optimize_resume(resume: str, industry: str, language: str):
    """优化简历"""
    analysis = analyze_resume(resume, industry, language)
    
    optimized = resume
    
    # 添加建议
    suggestions_text = "\n\n".join([s["suggestion"] for s in analysis["suggestions"]])
    
    return {
        "optimized_resume": optimized,
        "added_suggestions": suggestions_text,
        "score_improvement": f"建议添加{len(analysis['keywords_missing'])}个关键词",
        "analysis": analysis
    }

def check_ats(resume: str):
    """ATS兼容性检测"""
    score = 100
    
    if len(resume) < 200:
        score -= 20
    if len(resume) > 5000:
        score -= 10
    if not re.search(r'\d{11}', resume) and not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume):
        score -= 15
    if re.search(r'[◆●■□▲►]', resume):
        score -= 5
    
    return max(0, score)

def generate_suggestions(resume: str, missing_keywords: list, industry: str):
    """生成优化建议"""
    suggestions = []
    industry_data = KEYWORDS_DB.get(industry, {})
    
    for kw in missing_keywords[:5]:
        suggestions.append({
            "type": "add_keyword",
            "keyword": kw["keyword"],
            "suggestion": f"建议添加「{kw['keyword']}」相关经验描述"
        })
    
    if not re.search(r'\d+%', resume) and not re.search(r'\d+万', resume):
        metrics = industry_data.get("metrics_examples", [])
        if metrics:
            suggestions.append({
                "type": "add_metric",
                "suggestion": f"建议添加量化数据，如：{metrics[0]}"
            })
    
    return suggestions

# ========== 其他API ==========

@app.get("/")
async def root():
    return {
        "name": "ResumeAI API",
        "version": "2.0.0",
        "industries": list(KEYWORDS_DB.keys()),
        "auth_enabled": True
    }

@app.get("/api/v1/industries")
async def get_industries():
    industries = []
    for key, data in KEYWORDS_DB.items():
        industries.append({
            "id": key,
            "name": data.get("name", key),
            "name_en": data.get("name_en", key)
        })
    return {"success": True, "data": industries}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "keywords_loaded": len(KEYWORDS_DB),
        "auth_enabled": True,
        "data_dir": DATA_DIR,
        "db_path": USER_DB_PATH,
        "version": "2026-05-13-v2"  # 版本标记
    }

@app.get("/debug/db")
async def debug_db():
    """调试数据库状态"""
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        # 检查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        # 检查users表结构
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [row[1] for row in cursor.fetchall()]
        # 检查用户数量
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        return {
            "tables": tables,
            "users_columns": users_columns,
            "user_count": user_count,
            "db_path": USER_DB_PATH,
            "data_dir": DATA_DIR
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/debug/init-tables")
async def init_tables():
    """初始化/修复数据库表结构"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # 检查users表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 添加缺失的字段
        missing_columns = []
        
        if 'is_admin' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            missing_columns.append('is_admin')
        
        if 'is_paid' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_paid INTEGER DEFAULT 0")
            missing_columns.append('is_paid')
        
        # 创建verification_codes表
        cursor.execute('''CREATE TABLE IF NOT EXISTS verification_codes
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            code TEXT,
            expires_at TEXT,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        
        # 检查最终表结构
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [row[1] for row in cursor.fetchall()]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True, 
            "tables": tables,
            "users_columns": users_columns,
            "added_columns": missing_columns,
            "message": "数据库表结构已修复"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/debug/create-admin")
async def create_admin(
    email: str = Query(default="zhwffy@hotmail.com"),
    name: str = Query(default="Admin"),
    password: str = Query(default="Hiller")
):
    """创建管理员账号"""
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        
        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            # 更新为管理员
            cursor.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
            conn.commit()
            conn.close()
            return {"success": True, "message": "已将用户设置为管理员", "email": email}
        
        # 创建新管理员
        password_hash = hash_password(password)
        cursor.execute('''INSERT INTO users 
            (email, name, password_hash, is_admin, is_paid, created_at)
            VALUES (?, ?, ?, 1, 1, ?)''', 
            (email, name, password_hash, datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # 生成token
        token = create_token(user_id, email)
        
        return {
            "success": True,
            "message": "管理员账号已创建",
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
                "is_admin": True
            },
            "token": token
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/debug/test-email")
async def test_email(request: SendCodeRequest):
    """测试邮件发送"""
    try:
        code = generate_code(EMAIL_CONFIG["code_length"])
        result = send_verification_code(request.email, code)
        return {
            "success": result["success"],
            "message": result["message"],
            "test_mode": EMAIL_CONFIG["test_mode"],
            "smtp_server": EMAIL_CONFIG["smtp_server"],
            "smtp_user": EMAIL_CONFIG["smtp_user"],
            "error": result.get("error") if not result["success"] else None
        }
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": type(e).__name__}

@app.get("/debug/users")
async def debug_users():
    """查看所有用户"""
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, password_hash, created_at FROM users")
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row["id"],
                "email": row["email"],
                "name": row["name"],
                "password_hash": row["password_hash"],
                "created_at": row["created_at"]
            })
        conn.close()
        return {"users": users, "count": len(users)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/debug/check-password")
async def debug_check_password(email: str, password: str):
    """检查密码匹配"""
    try:
        conn = get_user_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {"error": "用户不存在", "email": email}
        
        stored_hash = user["password_hash"]
        input_hash = hash_password(password)
        
        return {
            "email": email,
            "stored_hash": stored_hash,
            "input_hash": input_hash,
            "match": stored_hash == input_hash,
            "password": password
        }
    except Exception as e:
        return {"error": str(e)}

# ========== 简历模板API ==========

RESUME_TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), "resume_templates.json")

def load_templates():
    """加载简历模板"""
    try:
        with open(RESUME_TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"templates": {}, "default_template": "classic"}

@app.get("/api/v1/templates")
async def get_templates():
    """获取所有简历模板"""
    templates_data = load_templates()
    return {
        "success": True,
        "templates": templates_data["templates"],
        "default": templates_data.get("default_template", "classic")
    }

@app.get("/api/v1/templates/{template_id}")
async def get_template(template_id: str):
    """获取单个模板详情"""
    templates_data = load_templates()
    template = templates_data["templates"].get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"success": True, "template": template}

@app.get("/api/v1/templates/recommend/{industry}")
async def recommend_template(industry: str):
    """根据行业推荐模板"""
    templates_data = load_templates()
    recommended = []
    for tid, template in templates_data["templates"].items():
        if industry in template.get("suitable_for", []):
            recommended.append({"id": tid, "name": template["name"], "match_score": 100})
    
    if not recommended:
        # 使用默认模板
        default_tid = templates_data.get("default_template", "classic")
        default_template = templates_data["templates"].get(default_tid)
        if default_template:
            recommended.append({"id": default_tid, "name": default_template["name"], "match_score": 50})
    
    return {
        "success": True,
        "industry": industry,
        "recommended": recommended
    }

# ========== 用户模板存储API ==========

class SaveTemplateRequest(BaseModel):
    template_id: str
    custom_settings: Optional[str] = "{}"  # JSON格式的自定义设置
    is_default: Optional[bool] = False

@app.post("/api/v1/user/templates")
async def save_user_template(request: SaveTemplateRequest, user: dict = Depends(get_current_user)):
    """保存用户模板偏好"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    user_id = user["id"]  # 使用正确的字段名
    
    # 检查是否已存在
    cursor.execute("SELECT id FROM user_templates WHERE user_id = ? AND template_id = ?", 
                   (user_id, request.template_id))
    existing = cursor.fetchone()
    
    if existing:
        # 更新
        cursor.execute('''UPDATE user_templates 
            SET custom_settings = ?, is_default = ?, updated_at = ?
            WHERE id = ?''',
            (request.custom_settings, 1 if request.is_default else 0, 
             datetime.now().isoformat(), existing["id"]))
    else:
        # 新建
        cursor.execute('''INSERT INTO user_templates 
            (user_id, template_id, custom_settings, is_default, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, request.template_id, request.custom_settings,
             1 if request.is_default else 0, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "模板已保存"}

@app.get("/api/v1/user/templates")
async def get_user_templates(user: dict = Depends(get_current_user)):
    """获取用户保存的模板列表"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    cursor.execute('''SELECT id, template_id, custom_settings, is_default, created_at 
        FROM user_templates WHERE user_id = ?''', (user["id"],))
    
    templates = []
    for row in cursor.fetchall():
        templates.append({
            "id": row["id"],
            "template_id": row["template_id"],
            "custom_settings": row["custom_settings"],
            "is_default": row["is_default"],
            "created_at": row["created_at"]
        })
    
    conn.close()
    return {"success": True, "templates": templates}

@app.delete("/api/v1/user/templates/{template_id}")
async def delete_user_template(template_id: int, user: dict = Depends(get_current_user)):
    """删除用户模板"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM user_templates WHERE id = ? AND user_id = ?", 
                   (template_id, user["id"]))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "模板已删除"}

# ========== 调试API ==========

@app.get("/api/v1/debug/status")
async def debug_status():
    """调试状态检查"""
    return {
        "success": True,
        "keywords_loaded": len(KEYWORDS_DB),
        "keywords_industries": list(KEYWORDS_DB.keys())[:10] if KEYWORDS_DB else [],
        "data_dir": DATA_DIR,
        "user_db_path": USER_DB_PATH,
        "has_sales": "sales" in KEYWORDS_DB,
        "jwt_secret": JWT_SECRET[:10] + "..."
    }

@app.post("/api/v1/debug/analyze")
async def debug_analyze():
    """调试简历分析"""
    try:
        # 测试分析函数
        test_resume = "张三销售经理电话13800138000"
        result = analyze_resume(test_resume, "sales", "zh", None)
        return {"success": True, "result": result}
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# ========== 支付API (LemonSqueezy) ==========

# LemonSqueezy配置（占位，需用户创建产品后替换）
LEMONSQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY", "")
LEMONSQUEEZY_STORE_ID = os.getenv("LEMONSQUEEZY_STORE_ID", "")
LEMONSQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

class CreateCheckoutRequest(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    email: Optional[str] = None

@app.get("/api/v1/payments/status")
async def payment_status():
    """检查支付配置状态"""
    return {
        "success": True,
        "configured": bool(LEMONSQUEEZY_API_KEY and LEMONSQUEEZY_STORE_ID),
        "store_id": LEMONSQUEEZY_STORE_ID if LEMONSQUEEZY_API_KEY else None,
        "message": "支付功能配置完成" if LEMONSQUEEZY_API_KEY else "请配置LemonSqueezy API Key和Store ID"
    }

@app.post("/api/v1/payments/checkout")
async def create_checkout(request: CreateCheckoutRequest, user: dict = Depends(get_current_user)):
    """创建支付checkout链接"""
    if not LEMONSQUEEZY_API_KEY or not LEMONSQUEEZY_STORE_ID:
        return {"error": "支付功能未配置，请联系管理员"}
    
    try:
        # LemonSqueezy Checkout API调用
        import httpx
        
        payload = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_data": {
                        "email": request.email or user["email"],
                        "custom": {
                            "user_id": str(user["id"])
                        }
                    }
                },
                "relationships": {
                    "store": {"type": "stores", "id": LEMONSQUEEZY_STORE_ID},
                    "variant": {"type": "variants", "id": request.variant_id or request.product_id}
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {LEMONSQUEEZY_API_KEY}",
            "Content-Type": "application/vnd.api+json"
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.lemonsqueezy.com/v1/checkouts",
                json=payload,
                headers=headers
            )
            
            if resp.status_code == 201:
                data = resp.json()
                checkout_url = data["data"]["attributes"]["url"]
                return {"success": True, "checkout_url": checkout_url}
            else:
                logger.error(f"LemonSqueezy checkout failed: {resp.text}")
                return {"error": "创建支付链接失败"}
    
    except Exception as e:
        logger.error(f"Payment error: {e}")
        return {"error": str(e)}

@app.post("/api/v1/payments/webhook")
async def payment_webhook(request: dict, x_signature: Optional[str] = Header(None)):
    """处理LemonSqueezy webhook回调"""
    # 验证签名
    if LEMONSQUEEZY_WEBHOOK_SECRET and x_signature:
        # TODO: 实现签名验证
        pass
    
    event_type = request.get("meta", {}).get("event_name", "")
    
    if event_type == "order_created":
        # 订单创建成功
        order_data = request["data"]["attributes"]
        custom_data = request["meta"]["custom_data"] or {}
        user_id = custom_data.get("user_id")
        
        if user_id:
            # 更新用户为付费用户
            conn = get_user_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET is_paid = 1 WHERE id = ?",
                (int(user_id),)
            )
            
            # 记录订单
            cursor.execute(
                "INSERT INTO orders (user_id, order_id, amount, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (int(user_id), order_data["order_id"], order_data["total"], "completed", datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            
            logger.info(f"Payment successful for user {user_id}")
    
    return {"success": True}

@app.get("/api/v1/user/orders")
async def get_user_orders(user: dict = Depends(get_current_user)):
    """获取用户订单历史"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 确保orders表存在
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        order_id TEXT,
        amount REAL,
        status TEXT,
        created_at TEXT)''')
    
    cursor.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (user["id"],)
    )
    
    orders = []
    for row in cursor.fetchall():
        orders.append({
            "id": row["id"],
            "order_id": row["order_id"],
            "amount": row["amount"],
            "status": row["status"],
            "created_at": row["created_at"]
        })
    
    conn.close()
    return {"success": True, "orders": orders}

# ========== 管理员API ==========

async def get_admin_user(authorization: Optional[str] = Header(None)):
    """验证管理员权限"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证token")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    
    conn = get_user_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (payload["user_id"],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    if not user["is_admin"]:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return dict(user)

@app.get("/api/v1/admin/stats")
async def admin_stats(admin: dict = Depends(get_admin_user)):
    """获取系统统计"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 用户统计
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_paid = 1")
    paid_users = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')")
    new_users_today = cursor.fetchone()["count"]
    
    # 使用统计
    cursor.execute("SELECT COUNT(*) as count FROM usage")
    total_usage = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM usage WHERE DATE(created_at) = DATE('now')")
    usage_today = cursor.fetchone()["count"]
    
    # 简历统计
    cursor.execute("SELECT COUNT(*) as count FROM resumes")
    total_resumes = cursor.fetchone()["count"]
    
    conn.close()
    
    return {
        "success": True,
        "data": {
            "users": {
                "total": total_users,
                "paid": paid_users,
                "free": total_users - paid_users,
                "new_today": new_users_today
            },
            "usage": {
                "total": total_usage,
                "today": usage_today
            },
            "resumes": {
                "total": total_resumes
            },
            "email_config": get_email_config()
        }
    }

@app.get("/api/v1/admin/users")
async def admin_list_users(admin: dict = Depends(get_admin_user)):
    """获取用户列表"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            u.id, u.email, u.name, u.is_paid, u.is_admin, u.created_at, u.last_login,
            (SELECT COUNT(*) FROM resumes WHERE user_id = u.id) as resume_count,
            (SELECT COUNT(*) FROM usage WHERE user_id = u.id) as usage_count
        FROM users u
        ORDER BY u.created_at DESC
    """)
    
    users = []
    for row in cursor.fetchall():
        users.append({
            "id": row["id"],
            "email": row["email"],
            "name": row["name"],
            "is_paid": bool(row["is_paid"]),
            "is_admin": bool(row["is_admin"]),
            "created_at": row["created_at"],
            "last_login": row["last_login"],
            "resume_count": row["resume_count"],
            "usage_count": row["usage_count"]
        })
    
    conn.close()
    return {"success": True, "data": users}

class UpdateUserRequest(BaseModel):
    is_paid: Optional[bool] = None
    is_admin: Optional[bool] = None

@app.put("/api/v1/admin/users/{user_id}")
async def admin_update_user(user_id: int, request: UpdateUserRequest, admin: dict = Depends(get_admin_user)):
    """更新用户状态"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if request.is_paid is not None:
        updates.append("is_paid = ?")
        params.append(1 if request.is_paid else 0)
    
    if request.is_admin is not None:
        updates.append("is_admin = ?")
        params.append(1 if request.is_admin else 0)
    
    if not updates:
        conn.close()
        raise HTTPException(status_code=400, detail="没有要更新的字段")
    
    params.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "用户已更新"}

@app.get("/api/v1/admin/usage")
async def admin_usage_logs(
    email: Optional[str] = None,
    action: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    admin: dict = Depends(get_admin_user)
):
    """获取使用日志（支持筛选）"""
    conn = get_user_db()
    cursor = conn.cursor()
    
    # 构建查询
    query = """
        SELECT 
            u.id, u.user_id, u.action, u.industry, u.created_at,
            us.email, us.name as user_name
        FROM usage u
        LEFT JOIN users us ON u.user_id = us.id
        WHERE 1=1
    """
    params = []
    
    if email:
        query += " AND us.email LIKE ?"
        params.append(f"%{email}%")
    
    if action:
        query += " AND u.action = ?"
        params.append(action)
    
    if date_from:
        query += " AND u.created_at >= ?"
        params.append(f"{date_from}T00:00:00")
    
    if date_to:
        query += " AND u.created_at <= ?"
        params.append(f"{date_to}T23:59:59")
    
    query += " ORDER BY u.created_at DESC LIMIT 200"
    
    cursor.execute(query, params)
    
    logs = []
    for row in cursor.fetchall():
        logs.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "email": row["email"] or "-",
            "user_name": row["user_name"] or "-",
            "action": row["action"],
            "industry": row["industry"],
            "created_at": row["created_at"]
        })
    
    conn.close()
    return {"success": True, "data": logs, "count": len(logs)}

class TestAIRequest(BaseModel):
    provider: str = "dashscope"
    model: str = "qwen-turbo"
    api_key: Optional[str] = None
    base_url: Optional[str] = None

@app.post("/api/v1/admin/test-ai")
async def admin_test_ai(request: TestAIRequest, admin: dict = Depends(get_admin_user)):
    """测试AI连接"""
    import httpx
    
    # 使用请求中的配置或默认配置
    api_key = request.api_key or DASHSCOPE_API_KEY
    base_url = request.base_url or DASHSCOPE_BASE_URL
    model = request.model or DASHSCOPE_MODEL
    
    if not api_key:
        return {"success": False, "error": "未配置API Key"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 ResumeAI/1.0"  # Coding API需要User-Agent
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "请回复：AI连接测试成功"}
                    ],
                    "max_tokens": 50
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"success": True, "response": reply, "model": model}
            else:
                error_msg = response.text[:200]
                return {"success": False, "error": f"API错误: {response.status_code} - {error_msg}"}
    except Exception as e:
        return {"success": False, "error": f"连接失败: {str(e)}"}

@app.get("/api/v1/admin/config")
async def admin_get_config(admin: dict = Depends(get_admin_user)):
    """获取系统配置"""
    config = {
        "email": {
            "smtp_server": EMAIL_CONFIG.get("smtp_server", ""),
            "smtp_port": EMAIL_CONFIG.get("smtp_port", 465),
            "smtp_user": EMAIL_CONFIG.get("smtp_user", ""),
            "configured": EMAIL_CONFIG.get("smtp_configured", False),
            "test_mode": EMAIL_CONFIG.get("test_mode", True)
        },
        "ai": {
            "provider": "coding",
            "model": DASHSCOPE_MODEL,
            "base_url": DASHSCOPE_BASE_URL,
            "configured": bool(DASHSCOPE_API_KEY)
        }
    }
    return {"success": True, "data": config}

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 ResumeAI Backend Starting...")
    print(f"Keywords loaded: {len(KEYWORDS_DB)} industries")
    print(f"Auth enabled: True")
    print(f"Free limit: {FREE_LIMIT} times/day")
    uvicorn.run(app, host="0.0.0.0", port=8001)

# Vercel Serverless Handler
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # 如果mangum未安装，提供一个基本的handler
    def handler(event, context):
        return {
            "statusCode": 500,
            "body": "Mangum not installed",
            "headers": {"Content-Type": "text/plain"}
        }