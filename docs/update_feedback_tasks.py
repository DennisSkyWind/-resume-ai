import json
from datetime import datetime

with open('feedback_tasks.json', 'r') as f:
    data = json.load(f)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 更新 T1-1, T1-2, T1-3, T1-4 为 completed
for task in data['tasks']:
    if task['id'] in ['T1-1', 'T1-2', 'T1-3', 'T1-4', 'T2-1', 'T2-2', 'T2-3', 'T2-4']:
        task['status'] = 'completed'
        task['completed_at'] = now

# 更新统计
completed = sum(1 for t in data['tasks'] if t['status'] == 'completed')
data['completed'] = completed
data['completion_rate'] = f'{completed}/{data["total_tasks"]}'
data['current_phase'] = 3

with open('feedback_tasks.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"任务状态已更新: {completed}/12 完成")