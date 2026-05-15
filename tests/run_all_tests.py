#!/usr/bin/env python3
"""
ResumeAI 自动化测试脚本
运行所有API和功能测试
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# 配置
API_BASE = "http://localhost:8001/api/v1"
ADMIN_API = "http://localhost:8001/api/v1/admin"
RESULTS_DIR = "/home/ubuntu/.openclaw/workspace/resume-ai/docs/test_results"

# 测试账号
TEST_USER = {
    "email": "test@example.com",
    "password": "test123456",
    "name": "测试用户"
}

ADMIN_USER = {
    "email": "zhwffy@hotmail.com",
    "password": "Hiller"
}

class TestRunner:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.token = None
        self.admin_token = None
        
        # 创建结果目录
        os.makedirs(RESULTS_DIR, exist_ok=True)
    
    def log(self, test_id, name, status, message="", duration=0):
        """记录测试结果"""
        result = {
            "test_id": test_id,
            "name": name,
            "status": status,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if status == "PASS":
            self.passed += 1
            print(f"✅ [{test_id}] {name} ({duration:.2f}s)")
        else:
            self.failed += 1
            print(f"❌ [{test_id}] {name}: {message}")
    
    def measure_time(self, func):
        """测量执行时间"""
        start = time.time()
        result = func()
        duration = time.time() - start
        return result, duration
    
    # ========== API测试 ==========
    
    def test_health(self):
        """测试服务健康状态"""
        test_id = "T15-0-0"
        try:
            res = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
            if res.status_code == 200:
                self.log(test_id, "服务健康检查", "PASS", "", 0)
            else:
                self.log(test_id, "服务健康检查", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "服务健康检查", "FAIL", str(e))
    
    def test_register(self):
        """测试注册API"""
        test_id = "T15-1-1"
        try:
            # 发送验证码
            res, duration = self.measure_time(lambda: requests.post(
                f"{API_BASE}/send-code",
                json={"email": TEST_USER["email"]},
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    self.log(test_id, "注册验证码发送", "PASS", "", duration)
                else:
                    self.log(test_id, "注册验证码发送", "FAIL", data.get("message", "未知错误"))
            else:
                self.log(test_id, "注册验证码发送", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "注册验证码发送", "FAIL", str(e))
    
    def test_login(self):
        """测试登录API"""
        test_id = "T15-1-1b"
        try:
            res, duration = self.measure_time(lambda: requests.post(
                f"{API_BASE}/login",
                json=ADMIN_USER,
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                token_data = data.get("data", {})
                if data.get("success") and token_data.get("token"):
                    self.token = token_data["token"]
                    self.admin_token = token_data["token"]  # 管理员token
                    self.log(test_id, "管理员登录", "PASS", "", duration)
                else:
                    self.log(test_id, "管理员登录", "FAIL", data.get("message", "无token"))
            else:
                self.log(test_id, "管理员登录", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "管理员登录", "FAIL", str(e))
    
    def test_user_info(self):
        """测试用户信息API"""
        test_id = "T15-1-1c"
        if not self.token:
            self.log(test_id, "获取用户信息", "FAIL", "无token")
            return
        
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{API_BASE}/me",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                user_data = data.get("data", {})
                if user_data.get("email") == ADMIN_USER["email"]:
                    self.log(test_id, "获取用户信息", "PASS", "", duration)
                else:
                    self.log(test_id, "获取用户信息", "FAIL", "邮箱不匹配")
            else:
                self.log(test_id, "获取用户信息", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "获取用户信息", "FAIL", str(e))
    
    def test_industries(self):
        """测试行业列表API"""
        test_id = "T15-1-2"
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{API_BASE}/industries",
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success") and len(data.get("data", [])) > 0:
                    self.log(test_id, "行业列表API", "PASS", f"行业数: {len(data['data'])}", duration)
                else:
                    self.log(test_id, "行业列表API", "FAIL", "无行业数据")
            else:
                self.log(test_id, "行业列表API", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "行业列表API", "FAIL", str(e))
    
    def test_feedback_submit(self):
        """测试反馈提交API"""
        test_id = "T15-1-5"
        try:
            res, duration = self.measure_time(lambda: requests.post(
                f"{API_BASE}/feedback",
                json={"type": "suggestion", "content": "自动化测试反馈"},
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    self.log(test_id, "反馈提交API", "PASS", "", duration)
                else:
                    self.log(test_id, "反馈提交API", "FAIL", data.get("message"))
            else:
                self.log(test_id, "反馈提交API", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "反馈提交API", "FAIL", str(e))
    
    # ========== 管理后台测试 ==========
    
    def test_admin_stats(self):
        """测试管理后台统计API"""
        test_id = "T15-3-2"
        if not self.admin_token:
            self.log(test_id, "管理员统计API", "FAIL", "无管理员token")
            return
        
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{ADMIN_API}/stats",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    self.log(test_id, "管理员统计API", "PASS", "", duration)
                else:
                    self.log(test_id, "管理员统计API", "FAIL", data.get("message"))
            else:
                self.log(test_id, "管理员统计API", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "管理员统计API", "FAIL", str(e))
    
    def test_admin_feedback(self):
        """测试管理员反馈列表API"""
        test_id = "T15-3-2b"
        if not self.admin_token:
            self.log(test_id, "管理员反馈列表API", "FAIL", "无管理员token")
            return
        
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{ADMIN_API}/feedback",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    count = len(data.get("data", []))
                    self.log(test_id, "管理员反馈列表API", "PASS", f"反馈数: {count}", duration)
                else:
                    self.log(test_id, "管理员反馈列表API", "FAIL", data.get("message"))
            else:
                self.log(test_id, "管理员反馈列表API", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "管理员反馈列表API", "FAIL", str(e))
    
    def test_admin_config(self):
        """测试管理员AI配置API"""
        test_id = "T15-3-3"
        if not self.admin_token:
            self.log(test_id, "管理员AI配置API", "FAIL", "无管理员token")
            return
        
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{ADMIN_API}/config",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                timeout=10
            ))
            
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    self.log(test_id, "管理员AI配置API", "PASS", "", duration)
                else:
                    self.log(test_id, "管理员AI配置API", "FAIL", data.get("message"))
            else:
                self.log(test_id, "管理员AI配置API", "FAIL", f"状态码: {res.status_code}")
        except Exception as e:
            self.log(test_id, "管理员AI配置API", "FAIL", str(e))
    
    # ========== 安全测试 ==========
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        test_id = "T15-5-1"
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{API_BASE}/me",
                timeout=10
            ))
            
            if res.status_code == 401:
                self.log(test_id, "未授权访问拦截", "PASS", "", duration)
            else:
                self.log(test_id, "未授权访问拦截", "FAIL", f"状态码应为401，实际: {res.status_code}")
        except Exception as e:
            self.log(test_id, "未授权访问拦截", "FAIL", str(e))
    
    def test_invalid_token(self):
        """测试无效Token"""
        test_id = "T15-5-1b"
        try:
            res, duration = self.measure_time(lambda: requests.get(
                f"{API_BASE}/me",
                headers={"Authorization": "Bearer invalid_token_12345"},
                timeout=10
            ))
            
            if res.status_code == 401:
                self.log(test_id, "无效Token拦截", "PASS", "", duration)
            else:
                self.log(test_id, "无效Token拦截", "FAIL", f"状态码应为401，实际: {res.status_code}")
        except Exception as e:
            self.log(test_id, "无效Token拦截", "FAIL", str(e))
    
    def run_all(self):
        """运行所有测试"""
        print("="*60)
        print(f"ResumeAI 自动化测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print()
        
        # 基础测试
        print(">>> 基础服务测试")
        self.test_health()
        
        # API测试
        print("\n>>> API接口测试")
        self.test_industries()
        self.test_register()
        self.test_login()
        self.test_user_info()
        self.test_feedback_submit()
        
        # 管理后台测试
        print("\n>>> 管理后台测试")
        self.test_admin_stats()
        self.test_admin_feedback()
        self.test_admin_config()
        
        # 安全测试
        print("\n>>> 安全测试")
        self.test_unauthorized_access()
        self.test_invalid_token()
        
        # 输出结果
        print()
        print("="*60)
        print(f"测试完成: 通过 {self.passed}, 失败 {self.failed}")
        print("="*60)
        
        # 保存结果
        self.save_results()
        
        return self.failed == 0
    
    def save_results(self):
        """保存测试结果"""
        filename = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(RESULTS_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump({
                "summary": {
                    "total": len(self.results),
                    "passed": self.passed,
                    "failed": self.failed,
                    "timestamp": datetime.now().isoformat()
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n结果已保存: {filepath}")

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)