import json

with open('/home/ubuntu/.openclaw/workspace/resume-ai/docs/task_status.json', 'r') as f:
    data = json.load(f)

# 添加测试任务到tasks数组
test_tasks = [
    {"id": "T15-1-1", "phase": "Phase 15", "name": "用户认证API测试", "description": "测试注册、登录、Token验证流程", "status": "pending", "priority": "high", "test_type": "api"},
    {"id": "T15-1-2", "phase": "Phase 15", "name": "简历分析API测试", "description": "测试PDF/Word上传解析、分析结果准确性", "status": "pending", "priority": "high", "test_type": "api"},
    {"id": "T15-1-3", "phase": "Phase 15", "name": "简历优化API测试", "description": "测试优化建议生成、模板输出", "status": "pending", "priority": "high", "test_type": "api"},
    {"id": "T15-1-4", "phase": "Phase 15", "name": "导出功能测试", "description": "测试PDF/Word导出格式和完整性", "status": "pending", "priority": "medium", "test_type": "api"},
    {"id": "T15-1-5", "phase": "Phase 15", "name": "反馈系统API测试", "description": "测试反馈提交和管理员管理功能", "status": "pending", "priority": "medium", "test_type": "api"},
    {"id": "T15-2-1", "phase": "Phase 15", "name": "新用户注册流程测试", "description": "测试完整注册流程用户体验", "status": "pending", "priority": "high", "test_type": "flow"},
    {"id": "T15-2-2", "phase": "Phase 15", "name": "简历分析完整流程测试", "description": "测试从上传到导出的完整流程", "status": "pending", "priority": "high", "test_type": "flow"},
    {"id": "T15-2-3", "phase": "Phase 15", "name": "简历优化完整流程测试", "description": "测试优化和模板导出流程", "status": "pending", "priority": "high", "test_type": "flow"},
    {"id": "T15-2-4", "phase": "Phase 15", "name": "使用次数限制测试", "description": "测试Free用户每日限制机制", "status": "pending", "priority": "medium", "test_type": "flow"},
    {"id": "T15-3-1", "phase": "Phase 15", "name": "管理员登录测试", "description": "测试管理员账号登录和权限", "status": "pending", "priority": "high", "test_type": "admin"},
    {"id": "T15-3-2", "phase": "Phase 15", "name": "统计数据测试", "description": "测试统计数据准确性和图表显示", "status": "pending", "priority": "medium", "test_type": "admin"},
    {"id": "T15-3-3", "phase": "Phase 15", "name": "AI配置编辑测试", "description": "测试模型切换和参数调整", "status": "pending", "priority": "medium", "test_type": "admin"},
    {"id": "T15-4-1", "phase": "Phase 15", "name": "API响应时间测试", "description": "测量各API响应时间，目标<2秒", "status": "pending", "priority": "medium", "test_type": "performance"},
    {"id": "T15-4-2", "phase": "Phase 15", "name": "文件处理性能测试", "description": "测试大文件上传和处理稳定性", "status": "pending", "priority": "medium", "test_type": "performance"},
    {"id": "T15-5-1", "phase": "Phase 15", "name": "认证安全测试", "description": "测试Token过期、未授权访问拦截", "status": "pending", "priority": "high", "test_type": "security"},
    {"id": "T15-5-2", "phase": "Phase 15", "name": "文件上传安全测试", "description": "测试文件类型验证和恶意文件拦截", "status": "pending", "priority": "high", "test_type": "security"}
]

data['tasks'].extend(test_tasks)
data['total_tasks'] = len(data['tasks'])
data['pending'] = sum(1 for t in data['tasks'] if t['status'] == 'pending')
data['completed'] = sum(1 for t in data['tasks'] if t['status'] == 'completed')

# 更新milestones
data['milestones']['M8']['status'] = 'completed'
data['milestones']['M9'] = {'name': '测试与优化', 'target': 'Phase 15完成', 'status': 'in_progress'}

with open('/home/ubuntu/.openclaw/workspace/resume-ai/docs/task_status.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'总任务: {data["total_tasks"]}')
print(f'已完成: {data["completed"]}')
print(f'待处理: {data["pending"]}')
print('Phase 15测试任务已添加!')