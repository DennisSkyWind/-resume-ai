import json

# 加载现有keywords.json
with open('keywords.json') as f:
    data = json.load(f)

# 定义子行业分类
sub_industries_map = {
    "sales": {
        "sub_industries": [
            {
                "id": "retail_sales",
                "name": "零售销售",
                "keywords_boost": ["门店销售", "顾客服务", "促销活动", "商品陈列"]
            },
            {
                "id": "b2b_sales",
                "name": "B2B销售",
                "keywords_boost": ["企业客户", "商务谈判", "合同签署", "解决方案"]
            },
            {
                "id": "channel_sales",
                "name": "渠道销售",
                "keywords_boost": ["代理商管理", "渠道拓展", "分销网络", "区域覆盖"]
            },
            {
                "id": "key_account",
                "name": "大客户销售",
                "keywords_boost": ["大客户管理", "战略客户", "高层对接", "定制方案"]
            }
        ]
    },
    "finance": {
        "sub_industries": [
            {
                "id": "accounting",
                "name": "会计",
                "keywords_boost": ["凭证录入", "账务处理", "财务报表", "科目核算"]
            },
            {
                "id": "auditing",
                "name": "审计",
                "keywords_boost": ["审计执行", "内控评估", "审计报告", "风险发现"]
            },
            {
                "id": "financial_analysis",
                "name": "财务分析",
                "keywords_boost": ["财务分析", "经营分析", "数据建模", "预测分析"]
            },
            {
                "id": "taxation",
                "name": "税务",
                "keywords_boost": ["税务筹划", "税务申报", "税务合规", "税收优惠"]
            }
        ]
    },
    "administrative": {
        "sub_industries": [
            {
                "id": "receptionist",
                "name": "前台接待",
                "keywords_boost": ["前台接待", "来访登记", "电话接听", "快递收发"]
            },
            {
                "id": "hr_assistant",
                "name": "人事助理",
                "keywords_boost": ["简历筛选", "面试安排", "入职办理", "档案管理"]
            },
            {
                "id": "admin_supervisor",
                "name": "行政主管",
                "keywords_boost": ["行政管理", "流程优化", "部门协调", "预算控制"]
            },
            {
                "id": "office_manager",
                "name": "办公室经理",
                "keywords_boost": ["办公环境", "资产管理", "供应商管理", "团队建设"]
            }
        ]
    }
}

# 更新行业数据
for industry_id, sub_data in sub_industries_map.items():
    if industry_id in data:
        data[industry_id]["sub_industries"] = sub_data["sub_industries"]

# 保存更新后的数据
with open('keywords.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"已更新 {len(sub_industries_map)} 个行业的子行业分类")
for ind_id, sub in sub_industries_map.items():
    print(f"  {ind_id}: {len(sub['sub_industries'])}个子行业")