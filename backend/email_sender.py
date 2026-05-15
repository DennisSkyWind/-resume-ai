#!/usr/bin/env python3
"""
邮箱验证码发送模块
支持Resend API发送
"""

import os
import random

# Resend API配置
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_ARxpVJ73_7nqzDoQoPkLdDaUe6budhJHP")

# 邮箱配置
EMAIL_CONFIG = {
    # Resend配置
    "resend_api_key": RESEND_API_KEY,
    "from_email": "noreply@bearai.bond",  # 已验证域名
    "from_name": "ResumeAI",
    
    # 测试模式（关闭，使用Resend真实发送）
    "test_mode": False,
    
    # 验证码配置
    "code_length": 6,
    "code_expire_minutes": 10,
    
    # 验证码内容
    "subject": "ResumeAI 验证码",
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
            "test_code": code
        }
    
    # 使用Resend API发送
    try:
        import resend
        
        # 设置API Key
        resend.api_key = EMAIL_CONFIG["resend_api_key"]
        
        body = f"""
您好！

您的ResumeAI注册验证码是：{code}

验证码有效期为{EMAIL_CONFIG['code_expire_minutes']}分钟，请尽快完成注册。

如果这不是您的操作，请忽略此邮件。

— ResumeAI团队
"""
        
        result = resend.Emails.send({
            "from": f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>",
            "to": [email],
            "subject": EMAIL_CONFIG["subject"],
            "text": body
        })
        
        print(f"Resend发送成功: {result}")
        return {
            "success": True,
            "message": "验证码已发送到邮箱",
            "email_id": result.get("id") if isinstance(result, dict) else str(result)
        }
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"发送失败: {str(e)}",
            "error": str(e),
            "error_type": type(e).__name__
        }

def get_email_config():
    """获取邮箱配置状态"""
    return {
        "test_mode": EMAIL_CONFIG["test_mode"],
        "resend_configured": bool(EMAIL_CONFIG["resend_api_key"]),
        "from_email": EMAIL_CONFIG["from_email"],
        "code_expire_minutes": EMAIL_CONFIG["code_expire_minutes"]
    }

def send_marketing_email(email: str, template_type: str, data: dict = {}) -> dict:
    """
    发送营销邮件
    template_type: 'usage_reminder', 'promo', 'welcome', 'upgrade_reminder'
    """
    
    templates = {
        'welcome': {
            'subject': '欢迎使用ResumeAI',
            'body': f"""
您好！

感谢您注册ResumeAI，我们很高兴为您服务！

ResumeAI是一款智能简历分析与优化工具，帮助您：
• 分析简历关键词匹配度
• 检查ATS格式兼容性
• 对比JD职位要求
• 获取优化建议

现在就开始使用：https://resume.bearai.bond

如有任何问题，欢迎随时联系我们。

— ResumeAI团队
"""
        },
        'usage_reminder': {
            'subject': 'ResumeAI使用提醒',
            'body': f"""
您好！

我们发现您已注册ResumeAI但尚未使用。

您的简历可能还有优化空间，立即分析可以获得：
• 关键词匹配分析
• ATS格式检查
• 专业优化建议

立即开始：https://resume.bearai.bond

— ResumeAI团队
"""
        },
        'upgrade_reminder': {
            'subject': '解锁更多功能',
            'body': f"""
您好！

您今日的使用次数即将用完。

升级会员可以获得：
• 更多每日使用次数
• 导出PDF/Word功能
• JD职位匹配分析
• 优先客服支持

升级会员：https://resume.bearai.bond

— ResumeAI团队
"""
        },
        'promo': {
            'subject': 'ResumeAI限时优惠',
            'body': f"""
您好！

ResumeAI限时优惠活动正在进行！

升级VIP会员享受：
• 无限使用次数
• 所有高级功能
• 专业简历模板

活动详情：https://resume.bearai.bond

— ResumeAI团队
"""
        }
    }
    
    template = templates.get(template_type)
    if not template:
        return {"success": False, "message": "未知邮件模板"}
    
    # 测试模式
    if EMAIL_CONFIG["test_mode"]:
        return {"success": True, "message": f"营销邮件已生成（测试模式）: {template_type}"}
    
    # 使用Resend发送
    try:
        import resend
        resend.api_key = EMAIL_CONFIG["resend_api_key"]
        
        result = resend.Emails.send({
            "from": f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email']}>",
            "to": [email],
            "subject": template["subject"],
            "text": template["body"]
        })
        
        return {
            "success": True,
            "message": "营销邮件已发送",
            "email_id": result.get("id") if isinstance(result, dict) else str(result)
        }
    except Exception as e:
        return {"success": False, "message": f"发送失败: {str(e)}"}