#!/usr/bin/env python3
"""
邮箱验证码发送模块
支持SMTP发送和本地测试模式
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random

# 邮箱配置（163邮箱）
EMAIL_CONFIG = {
    # SMTP配置
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,  # SSL端口
    "smtp_user": "zhwffy@163.com",
    "smtp_password": "BAQesckiq8fTrUXY",  # 授权码
    "smtp_configured": True,  # 已配置
    
    # 测试模式（开启，验证码返回给前端）
    "test_mode": True,  # 生产环境先用测试模式
    
    # 验证码配置
    "code_length": 6,
    "code_expire_minutes": 10,
    
    # 验证码内容
    "subject": "ResumeAI 邮箱验证码",
    "from_name": "ResumeAI"
}

def generate_code(length=6):
    """生成随机验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_verification_code(email: str, code: str) -> dict:
    """
    发送验证码邮件
    返回: {"success": bool, "message": str, "code": str（测试模式）}
    """
    
    # 测试模式：不实际发送，返回验证码
    if EMAIL_CONFIG["test_mode"]:
        print(f"[TEST MODE] 验证码: {code} -> {email}")
        return {
            "success": True,
            "message": "验证码已生成（测试模式）",
            "test_code": code  # 测试模式返回验证码供前端显示
        }
    
    # 实际发送邮件
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['smtp_user']}>"
        msg['To'] = email
        msg['Subject'] = EMAIL_CONFIG['subject']
        
        body = f"""
您好！

您的ResumeAI注册验证码是：{code}

验证码有效期为{EMAIL_CONFIG['code_expire_minutes']}分钟，请尽快完成注册。

如果这不是您的操作，请忽略此邮件。

— ResumeAI团队
"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件（SSL方式，163邮箱需要）
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_password'])
        server.send_message(msg)
        server.quit()
        
        return {"success": True, "message": "验证码已发送到邮箱"}
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return {"success": False, "message": f"发送失败: {str(e)}"}

def get_email_config():
    """获取邮箱配置状态"""
    return {
        "test_mode": EMAIL_CONFIG["test_mode"],
        "smtp_configured": bool(EMAIL_CONFIG["smtp_server"] and EMAIL_CONFIG["smtp_user"]),
        "code_expire_minutes": EMAIL_CONFIG["code_expire_minutes"]
    }