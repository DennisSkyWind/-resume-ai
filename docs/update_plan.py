#!/usr/bin/env python3
import json
from datetime import datetime

# 读取现有计划
d = json.load(open('/home/ubuntu/.openclaw/workspace/resume-ai/docs/task_status.json'))

# 新增任务 - 完善开发计划
new_tasks = [
    # Phase 7: 用户端等级功能完善
    {"id": "T7-1-1", "phase": "Phase 7", "name": "用户端等级信息展示", "description": "首页显示用户当前等级、剩余使用次数、到期时间", "status": "pending", "priority": "high"},
    {"id": "T7-1-2", "phase": "Phase 7", "name": "等级升级引导页面", "description": "设计等级升级页面，展示各等级权益对比", "status": "pending", "priority": "high"},
    {"id": "T7-1-3", "phase": "Phase 7", "name": "用户API返回等级信息", "description": "登录/me API返回user_level、daily_limit_remaining等", "status": "pending", "priority": "high"},
    
    # Phase 8: 简历导出与模板下载
    {"id": "T8-1-1", "phase": "Phase 8", "name": "简历导出PDF功能", "description": "将优化后的简历导出为专业PDF格式", "status": "pending", "priority": "high"},
    {"id": "T8-1-2", "phase": "Phase 8", "name": "简历导出Word功能", "description": "导出为可编辑的Word文档", "status": "pending", "priority": "high"},
    {"id": "T8-2-1", "phase": "Phase 8", "name": "模板下载功能", "description": "用户可选择模板下载空白简历模板", "status": "pending", "priority": "medium"},
    {"id": "T8-2-2", "phase": "Phase 8", "name": "模板定制功能", "description": "用户可自定义模板颜色、字体等", "status": "pending", "priority": "medium"},
    
    # Phase 9: 支付系统集成
    {"id": "T9-1-1", "phase": "Phase 9", "name": "支付平台选择与接入", "description": "接入虎皮椒(国内)或Stripe(海外)支付", "status": "pending", "priority": "high"},
    {"id": "T9-1-2", "phase": "Phase 9", "name": "订单管理系统", "description": "创建orders表，记录支付订单状态", "status": "pending", "priority": "high"},
    {"id": "T9-1-3", "phase": "Phase 9", "name": "支付回调处理", "description": "处理支付成功回调，自动升级用户等级", "status": "pending", "priority": "high"},
    {"id": "T9-2-1", "phase": "Phase 9", "name": "前端支付页面", "description": "设计支付流程页面，支持多种支付方式", "status": "pending", "priority": "high"},
    {"id": "T9-2-2", "phase": "Phase 9", "name": "订单历史查看", "description": "用户可查看支付历史和发票", "status": "pending", "priority": "medium"},
    
    # Phase 10: 高级功能
    {"id": "T10-1-1", "phase": "Phase 10", "name": "JD匹配度分析", "description": "分析简历与目标职位的匹配度评分", "status": "pending", "priority": "high"},
    {"id": "T10-1-2", "phase": "Phase 10", "name": "缺失关键词提示", "description": "对比JD指出简历中缺失的关键技能", "status": "pending", "priority": "high"},
    {"id": "T10-2-1", "phase": "Phase 10", "name": "邀请好友系统", "description": "用户邀请好友注册获得额外使用次数", "status": "pending", "priority": "medium"},
    {"id": "T10-2-2", "phase": "Phase 10", "name": "邀请码生成与验证", "description": "每个用户有专属邀请码", "status": "pending", "priority": "medium"},
    
    # Phase 11: 用户体验优化
    {"id": "T11-1-1", "phase": "Phase 11", "name": "移动端适配优化", "description": "优化手机端使用体验", "status": "pending", "priority": "high"},
    {"id": "T11-1-2", "phase": "Phase 11", "name": "新手引导优化", "description": "完善首次使用引导流程", "status": "pending", "priority": "medium"},
    {"id": "T11-2-1", "phase": "Phase 11", "name": "多语言支持完善", "description": "前端界面支持中英文切换", "status": "pending", "priority": "medium"},
    {"id": "T11-2-2", "phase": "Phase 11", "name": "分析结果可视化", "description": "评分、关键词匹配用图表展示", "status": "pending", "priority": "medium"},
    
    # Phase 12: 运营与营销功能
    {"id": "T12-1-1", "phase": "Phase 12", "name": "用户行为分析", "description": "统计用户使用习惯、流失率等", "status": "pending", "priority": "medium"},
    {"id": "T12-1-2", "phase": "Phase 12", "name": "邮件营销功能", "description": "定期发送使用提醒、促销邮件", "status": "pending", "priority": "low"},
    {"id": "T12-2-1", "phase": "Phase 12", "name": "SEO优化", "description": "优化网站SEO，提升搜索排名", "status": "pending", "priority": "medium"},
    {"id": "T12-2-2", "phase": "Phase 12", "name": "帮助文档页面", "description": "创建使用指南和常见问题页面", "status": "pending", "priority": "low"},
    
    # Phase 13: 系统稳定性
    {"id": "T13-1-1", "phase": "Phase 13", "name": "错误监控与日志", "description": "集成错误监控，记录系统异常", "status": "pending", "priority": "high"},
    {"id": "T13-1-2", "phase": "Phase 13", "name": "数据备份机制", "description": "定期备份用户数据库", "status": "pending", "priority": "high"},
    {"id": "T13-2-1", "phase": "Phase 13", "name": "API限流保护", "description": "防止恶意请求，保护API", "status": "pending", "priority": "medium"},
    {"id": "T13-2-2", "phase": "Phase 13", "name": "性能优化", "description": "优化API响应速度，减少加载时间", "status": "pending", "priority": "medium"},
]

# 添加创建时间
for t in new_tasks:
    t['created_at'] = datetime.now().isoformat()

# 添加新任务
for t in new_tasks:
    d['tasks'].append(t)

# 更新总任务数
d['total_tasks'] = len(d['tasks'])
d['version'] = '2.0'
d['last_updated'] = datetime.now().isoformat()
d['milestones'] = {
    "M1": {"name": "基础功能上线", "target": "Phase 1-5完成", "status": "completed"},
    "M2": {"name": "管理后台完成", "target": "Phase 6完成", "status": "completed"},
    "M3": {"name": "支付系统集成", "target": "Phase 9完成", "status": "pending"},
    "M4": {"name": "高级功能完善", "target": "Phase 10完成", "status": "pending"},
    "M5": {"name": "用户体验优化", "target": "Phase 11完成", "status": "pending"},
    "M6": {"name": "运营体系建立", "target": "Phase 12完成", "status": "pending"}
}

# 保存
json.dump(d, open('/home/ubuntu/.openclaw/workspace/resume-ai/docs/task_status.json', 'w'), indent=2)

completed = len([t for t in d['tasks'] if t['status'] == 'completed'])
print(f'开发计划更新完成!')
print(f'总任务数: {d["total_tasks"]}')
print(f'已完成: {completed}')
print(f'进度: {completed}/{d["total_tasks"]} ({completed*100//d["total_tasks"]}%)')
print()
print('新增Phase:')
for phase in ['Phase 7', 'Phase 8', 'Phase 9', 'Phase 10', 'Phase 11', 'Phase 12', 'Phase 13']:
    count = len([t for t in new_tasks if t['phase'] == phase])
    print(f'{phase}: {count}任务')
print()
print('新增任务总数:', len(new_tasks))