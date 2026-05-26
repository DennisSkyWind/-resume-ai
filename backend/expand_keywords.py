import json

# 加载现有关键词库
with open('keywords.json') as f:
    data = json.load(f)

# 定义扩展关键词（每个行业扩展到50+关键词）
keyword_expansions = {
    "sales": {
        "required": [
            {"keyword": "客户开发", "weight": 10},
            {"keyword": "销售目标", "weight": 10},
            {"keyword": "业绩增长", "weight": 9},
            {"keyword": "渠道拓展", "weight": 9},
            {"keyword": "客户关系", "weight": 9},
            {"keyword": "商务谈判", "weight": 8},
            {"keyword": "合同签署", "weight": 8},
            {"keyword": "销售计划", "weight": 8},
            {"keyword": "市场分析", "weight": 8},
            {"keyword": "竞品分析", "weight": 7},
            {"keyword": "销售预测", "weight": 7},
            {"keyword": "客户拜访", "weight": 7},
            {"keyword": "销售漏斗", "weight": 7},
            {"keyword": "客户转化", "weight": 7},
            {"keyword": "销售复盘", "weight": 6},
            {"keyword": "团队激励", "weight": 6},
            {"keyword": "销售培训", "weight": 6},
            {"keyword": "客户分层", "weight": 6},
            {"keyword": "销售策略", "weight": 6},
            {"keyword": "客户维护", "weight": 6}
        ],
        "preferred": [
            {"keyword": "CRM", "weight": 5},
            {"keyword": "大客户管理", "weight": 5},
            {"keyword": "销售报表", "weight": 5},
            {"keyword": "客户画像", "weight": 5},
            {"keyword": "销售跟进", "weight": 5},
            {"keyword": "客户满意度", "weight": 4},
            {"keyword": "销售激励", "weight": 4},
            {"keyword": "客户回访", "weight": 4},
            {"keyword": "销售数据", "weight": 4},
            {"keyword": "客户投诉处理", "weight": 4},
            {"keyword": "销售会议", "weight": 4},
            {"keyword": "客户需求分析", "weight": 4},
            {"keyword": "销售工具", "weight": 3},
            {"keyword": "客户档案", "weight": 3},
            {"keyword": "销售PPT", "weight": 3},
            {"keyword": "客户推荐", "weight": 3},
            {"keyword": "销售案例", "weight": 3},
            {"keyword": "客户续约", "weight": 3},
            {"keyword": "销售演示", "weight": 3},
            {"keyword": "客户转介绍", "weight": 3},
            {"keyword": "销售话术", "weight": 3},
            {"keyword": "客户痛点", "weight": 3},
            {"keyword": "销售提案", "weight": 3},
            {"keyword": "客户预算", "weight": 3},
            {"keyword": "销售跟进记录", "weight": 3},
            {"keyword": "客户异议处理", "weight": 3}
        ]
    },
    "finance": {
        "required": [
            {"keyword": "财务报表", "weight": 10},
            {"keyword": "预算管理", "weight": 10},
            {"keyword": "成本控制", "weight": 9},
            {"keyword": "税务筹划", "weight": 9},
            {"keyword": "内部控制", "weight": 9},
            {"keyword": "财务分析", "weight": 9},
            {"keyword": "资金管理", "weight": 8},
            {"keyword": "会计核算", "weight": 8},
            {"keyword": "财务合规", "weight": 8},
            {"keyword": "现金流管理", "weight": 8},
            {"keyword": "资产管理", "weight": 7},
            {"keyword": "财务预算", "weight": 7},
            {"keyword": "成本核算", "weight": 7},
            {"keyword": "财务审计", "weight": 7},
            {"keyword": "账务处理", "weight": 7},
            {"keyword": "财务预测", "weight": 6},
            {"keyword": "费用报销", "weight": 6},
            {"keyword": "财务制度", "weight": 6},
            {"keyword": "利润分析", "weight": 6},
            {"keyword": "财务风险", "weight": 6}
        ],
        "preferred": [
            {"keyword": "CPA", "weight": 5},
            {"keyword": "ACCA", "weight": 5},
            {"keyword": "财务软件", "weight": 5},
            {"keyword": "Excel财务", "weight": 5},
            {"keyword": "财务建模", "weight": 5},
            {"keyword": "税务申报", "weight": 4},
            {"keyword": "财务报告", "weight": 4},
            {"keyword": "成本优化", "weight": 4},
            {"keyword": "财务流程", "weight": 4},
            {"keyword": "资金调配", "weight": 4},
            {"keyword": "财务指标", "weight": 4},
            {"keyword": "账目核对", "weight": 4},
            {"keyword": "财务系统", "weight": 3},
            {"keyword": "税务合规", "weight": 3},
            {"keyword": "财务档案", "weight": 3},
            {"keyword": "成本分摊", "weight": 3},
            {"keyword": "财务培训", "weight": 3},
            {"keyword": "税务咨询", "weight": 3},
            {"keyword": "财务审批", "weight": 3},
            {"keyword": "成本降低", "weight": 3},
            {"keyword": "财务决策支持", "weight": 3},
            {"keyword": "税务风险", "weight": 3},
            {"keyword": "财务KPI", "weight": 3},
            {"keyword": "成本效益分析", "weight": 3},
            {"keyword": "财务数据可视化", "weight": 3},
            {"keyword": "税务优惠政策", "weight": 3}
        ]
    },
    "administrative": {
        "required": [
            {"keyword": "日程管理", "weight": 9},
            {"keyword": "会议组织", "weight": 9},
            {"keyword": "文档管理", "weight": 9},
            {"keyword": "跨部门协调", "weight": 9},
            {"keyword": "行政支持", "weight": 8},
            {"keyword": "接待服务", "weight": 8},
            {"keyword": "办公环境管理", "weight": 8},
            {"keyword": "行政流程优化", "weight": 8},
            {"keyword": "会议纪要", "weight": 7},
            {"keyword": "来访登记", "weight": 7},
            {"keyword": "办公用品采购", "weight": 7},
            {"keyword": "文件归档", "weight": 7},
            {"keyword": "部门协调", "weight": 7},
            {"keyword": "行政预算", "weight": 7},
            {"keyword": "办公设备管理", "weight": 6},
            {"keyword": "会议室预订", "weight": 6},
            {"keyword": "档案管理", "weight": 6},
            {"keyword": "行政制度", "weight": 6},
            {"keyword": "员工服务", "weight": 6},
            {"keyword": "行政效率", "weight": 6}
        ],
        "preferred": [
            {"keyword": "流程优化", "weight": 5},
            {"keyword": "成本节约", "weight": 5},
            {"keyword": "OA系统", "weight": 5},
            {"keyword": "办公自动化", "weight": 5},
            {"keyword": "行政报表", "weight": 5},
            {"keyword": "会议安排", "weight": 4},
            {"keyword": "文档规范", "weight": 4},
            {"keyword": "行政培训", "weight": 4},
            {"keyword": "办公用品发放", "weight": 4},
            {"keyword": "快递收发", "weight": 4},
            {"keyword": "行政采购", "weight": 4},
            {"keyword": "会议通知", "weight": 3},
            {"keyword": "文件传阅", "weight": 3},
            {"keyword": "行政审批", "weight": 3},
            {"keyword": "办公区域维护", "weight": 3},
            {"keyword": "考勤管理", "weight": 3},
            {"keyword": "行政数据分析", "weight": 3},
            {"keyword": "文件签发", "weight": 3},
            {"keyword": "行政工作计划", "weight": 3},
            {"keyword": "办公设备维护", "weight": 3},
            {"keyword": "行政服务满意度", "weight": 3},
            {"keyword": "会议设备调试", "weight": 3},
            {"keyword": "文件分发", "weight": 3},
            {"keyword": "行政采购审批", "weight": 3},
            {"keyword": "办公环境优化", "weight": 3},
            {"keyword": "行政台账", "weight": 3}
        ]
    }
}

# 新增热门行业
new_industries = {
    "new_media": {
        "name": "新媒体运营",
        "name_en": "New Media Operations",
        "keywords": {
            "required": [
                {"keyword": "内容策划", "weight": 10},
                {"keyword": "短视频运营", "weight": 10},
                {"keyword": "公众号运营", "weight": 9},
                {"keyword": "抖音运营", "weight": 9},
                {"keyword": "小红书运营", "weight": 9},
                {"keyword": "内容创作", "weight": 9},
                {"keyword": "流量增长", "weight": 8},
                {"keyword": "粉丝互动", "weight": 8},
                {"keyword": "热点追踪", "weight": 8},
                {"keyword": "数据分析", "weight": 8},
                {"keyword": "文案撰写", "weight": 7},
                {"keyword": "视频剪辑", "weight": 7},
                {"keyword": "直播策划", "weight": 7},
                {"keyword": "社群运营", "weight": 7},
                {"keyword": "话题营销", "weight": 7},
                {"keyword": "内容分发", "weight": 6},
                {"keyword": "用户画像", "weight": 6},
                {"keyword": "爆款内容", "weight": 6},
                {"keyword": "平台规则", "weight": 6},
                {"keyword": "涨粉策略", "weight": 6}
            ],
            "preferred": [
                {"keyword": "PR剪辑", "weight": 5},
                {"keyword": "封面设计", "weight": 5},
                {"keyword": "标题优化", "weight": 5},
                {"keyword": "评论区维护", "weight": 5},
                {"keyword": "内容矩阵", "weight": 5},
                {"keyword": "私域流量", "weight": 4},
                {"keyword": "内容复盘", "weight": 4},
                {"keyword": "平台算法", "weight": 4},
                {"keyword": "达人合作", "weight": 4},
                {"keyword": "内容投放", "weight": 4},
                {"keyword": "选题规划", "weight": 3},
                {"keyword": "内容模板", "weight": 3},
                {"keyword": "粉丝画像", "weight": 3},
                {"keyword": "热点蹭流量", "weight": 3},
                {"keyword": "内容节奏", "weight": 3},
                {"keyword": "平台运营规则", "weight": 3},
                {"keyword": "视频脚本", "weight": 3},
                {"keyword": "内容审核", "weight": 3},
                {"keyword": "账号定位", "weight": 3},
                {"keyword": "内容KPI", "weight": 3},
                {"keyword": "爆款分析", "weight": 3},
                {"keyword": "粉丝运营", "weight": 3},
                {"keyword": "内容选题库", "weight": 3},
                {"keyword": "平台变现", "weight": 3},
                {"keyword": "直播脚本", "weight": 3},
                {"keyword": "内容优化迭代", "weight": 3}
            ]
        },
        "metrics_examples": ["抖音账号涨粉50万+", "爆款视频播放量1000万"],
        "suitable_for": ["本科应届", "有经验"]
    },
    "live_streaming": {
        "name": "直播主播",
        "name_en": "Live Streaming Host",
        "keywords": {
            "required": [
                {"keyword": "直播带货", "weight": 10},
                {"keyword": "产品讲解", "weight": 10},
                {"keyword": "互动控场", "weight": 9},
                {"keyword": "直播间运营", "weight": 9},
                {"keyword": "销售转化", "weight": 9},
                {"keyword": "粉丝维护", "weight": 8},
                {"keyword": "直播脚本", "weight": 8},
                {"keyword": "话术技巧", "weight": 8},
                {"keyword": "产品演示", "weight": 8},
                {"keyword": "直播数据", "weight": 7},
                {"keyword": "观众互动", "weight": 7},
                {"keyword": "带货GMV", "weight": 7},
                {"keyword": "直播节奏", "weight": 7},
                {"keyword": "促销策划", "weight": 7},
                {"keyword": "直播复盘", "weight": 6},
                {"keyword": "粉丝增长", "weight": 6},
                {"keyword": "直播间布置", "weight": 6},
                {"keyword": "产品选品", "weight": 6},
                {"keyword": "直播时长", "weight": 6},
                {"keyword": "成交转化率", "weight": 6}
            ],
            "preferred": [
                {"keyword": "直播话术", "weight": 5},
                {"keyword": "产品卖点", "weight": 5},
                {"keyword": "直播间氛围", "weight": 5},
                {"keyword": "粉丝福利", "weight": 5},
                {"keyword": "直播预告", "weight": 5},
                {"keyword": "观众留存", "weight": 4},
                {"keyword": "产品价格策略", "weight": 4},
                {"keyword": "直播活动策划", "weight": 4},
                {"keyword": "粉丝互动话术", "weight": 4},
                {"keyword": "直播成交", "weight": 4},
                {"keyword": "主播形象", "weight": 3},
                {"keyword": "直播设备", "weight": 3},
                {"keyword": "产品库存", "weight": 3},
                {"keyword": "粉丝社群", "weight": 3},
                {"keyword": "直播排期", "weight": 3},
                {"keyword": "产品组合", "weight": 3},
                {"keyword": "直播间流量", "weight": 3},
                {"keyword": "粉丝复购", "weight": 3},
                {"keyword": "直播优惠", "weight": 3},
                {"keyword": "产品品牌", "weight": 3},
                {"keyword": "直播间点击率", "weight": 3},
                {"keyword": "粉丝购买力", "weight": 3},
                {"keyword": "直播互动率", "weight": 3},
                {"keyword": "产品对比", "weight": 3},
                {"keyword": "直播PK", "weight": 3},
                {"keyword": "粉丝抽奖", "weight": 3}
            ]
        },
        "metrics_examples": ["单场直播GMV破100万", "粉丝增长10万+"],
        "suitable_for": ["本科应届", "有经验"]
    },
    "cross_border_ecommerce": {
        "name": "跨境电商",
        "name_en": "Cross-border E-commerce",
        "keywords": {
            "required": [
                {"keyword": "跨境电商运营", "weight": 10},
                {"keyword": "亚马逊运营", "weight": 10},
                {"keyword": "产品上架", "weight": 9},
                {"keyword": "海外市场", "weight": 9},
                {"keyword": "店铺管理", "weight": 9},
                {"keyword": "订单处理", "weight": 8},
                {"keyword": "物流发货", "weight": 8},
                {"keyword": "客服沟通", "weight": 8},
                {"keyword": "选品分析", "weight": 8},
                {"keyword": "关键词优化", "weight": 7},
                {"keyword": "Listing优化", "weight": 7},
                {"keyword": "广告投放", "weight": 7},
                {"keyword": "库存管理", "weight": 7},
                {"keyword": "竞品分析", "weight": 7},
                {"keyword": "价格策略", "weight": 6},
                {"keyword": "海外仓储", "weight": 6},
                {"keyword": "品牌推广", "weight": 6},
                {"keyword": "市场调研", "weight": 6},
                {"keyword": "产品描述", "weight": 6},
                {"keyword": "跨境物流", "weight": 6}
            ],
            "preferred": [
                {"keyword": "FBA", "weight": 5},
                {"keyword": "FBM", "weight": 5},
                {"keyword": "Amazon Ads", "weight": 5},
                {"keyword": "ERP系统", "weight": 5},
                {"keyword": "海关申报", "weight": 5},
                {"keyword": "跨境支付", "weight": 4},
                {"keyword": "海外SEO", "weight": 4},
                {"keyword": "客户评价", "weight": 4},
                {"keyword": "产品摄影", "weight": 4},
                {"keyword": "汇率管理", "weight": 4},
                {"keyword": "FBA备货", "weight": 3},
                {"keyword": "海外客服", "weight": 3},
                {"keyword": "产品标签", "weight": 3},
                {"keyword": "跨境电商平台", "weight": 3},
                {"keyword": "海外用户画像", "weight": 3},
                {"keyword": "Listing评分", "weight": 3},
                {"keyword": "跨境税务", "weight": 3},
                {"keyword": "海外促销", "weight": 3},
                {"keyword": "产品包装", "weight": 3},
                {"keyword": "跨境退货", "weight": 3},
                {"keyword": "亚马逊算法", "weight": 3},
                {"keyword": "海外消费者", "weight": 3},
                {"keyword": "产品差异化", "weight": 3},
                {"keyword": "跨境资金流转", "weight": 3},
                {"keyword": "海外市场趋势", "weight": 3},
                {"keyword": "产品合规", "weight": 3}
            ]
        },
        "metrics_examples": ["月销售额$50万+", "店铺评分4.8分"],
        "suitable_for": ["本科应届", "有经验"]
    },
    "medical_sales": {
        "name": "医疗销售",
        "name_en": "Medical Sales",
        "keywords": {
            "required": [
                {"keyword": "医院客户开发", "weight": 10},
                {"keyword": "医疗器械销售", "weight": 10},
                {"keyword": "药品推广", "weight": 9},
                {"keyword": "科室拜访", "weight": 9},
                {"keyword": "医生沟通", "weight": 9},
                {"keyword": "产品学术推广", "weight": 8},
                {"keyword": "医院关系维护", "weight": 8},
                {"keyword": "招投标", "weight": 8},
                {"keyword": "医疗设备演示", "weight": 8},
                {"keyword": "销售业绩", "weight": 7},
                {"keyword": "医疗行业知识", "weight": 7},
                {"keyword": "客户需求分析", "weight": 7},
                {"keyword": "医院采购流程", "weight": 7},
                {"keyword": "产品培训", "weight": 7},
                {"keyword": "医疗展会", "weight": 6},
                {"keyword": "竞品分析", "weight": 6},
                {"keyword": "医院覆盖", "weight": 6},
                {"keyword": "销售回款", "weight": 6},
                {"keyword": "科室合作", "weight": 6},
                {"keyword": "医疗法规", "weight": 6}
            ],
            "preferred": [
                {"keyword": "GSP认证", "weight": 5},
                {"keyword": "医疗器械注册证", "weight": 5},
                {"keyword": "学术会议", "weight": 5},
                {"keyword": "临床试验", "weight": 5},
                {"keyword": "医院进院", "weight": 5},
                {"keyword": "医疗招标", "weight": 4},
                {"keyword": "科室主任沟通", "weight": 4},
                {"keyword": "产品适应症", "weight": 4},
                {"keyword": "医院谈判", "weight": 4},
                {"keyword": "医疗渠道", "weight": 4},
                {"keyword": "医药代表", "weight": 3},
                {"keyword": "医疗销售培训", "weight": 3},
                {"keyword": "医院拜访记录", "weight": 3},
                {"keyword": "产品临床数据", "weight": 3},
                {"keyword": "医疗采购周期", "weight": 3},
                {"keyword": "医院合作项目", "weight": 3},
                {"keyword": "医疗销售团队", "weight": 3},
                {"keyword": "产品技术参数", "weight": 3},
                {"keyword": "医院用药数据", "weight": 3},
                {"keyword": "医疗销售复盘", "weight": 3},
                {"keyword": "科室覆盖率", "weight": 3},
                {"keyword": "医疗销售政策", "weight": 3},
                {"keyword": "医院供应商", "weight": 3},
                {"keyword": "产品竞争优势", "weight": 3},
                {"keyword": "医疗行业趋势", "weight": 3},
                {"keyword": "医院客户档案", "weight": 3}
            ]
        },
        "metrics_examples": ["年度销售额1000万+", "覆盖医院50+家"],
        "suitable_for": ["本科应届", "有经验"]
    },
    "real_estate_sales": {
        "name": "房地产销售",
        "name_en": "Real Estate Sales",
        "keywords": {
            "required": [
                {"keyword": "房产销售", "weight": 10},
                {"keyword": "客户接待", "weight": 10},
                {"keyword": "楼盘讲解", "weight": 9},
                {"keyword": "客户跟进", "weight": 9},
                {"keyword": "成交签约", "weight": 9},
                {"keyword": "房源推荐", "weight": 8},
                {"keyword": "客户需求分析", "weight": 8},
                {"keyword": "房产政策解读", "weight": 8},
                {"keyword": "销售业绩", "weight": 8},
                {"keyword": "客户维护", "weight": 7},
                {"keyword": "带看房源", "weight": 7},
                {"keyword": "贷款咨询", "weight": 7},
                {"keyword": "房产过户", "weight": 7},
                {"keyword": "客户谈判", "weight": 7},
                {"keyword": "市场分析", "weight": 6},
                {"keyword": "房源储备", "weight": 6},
                {"keyword": "购房流程", "weight": 6},
                {"keyword": "客户转介绍", "weight": 6},
                {"keyword": "房产证办理", "weight": 6},
                {"keyword": "销售数据", "weight": 6}
            ],
            "preferred": [
                {"keyword": "VR看房", "weight": 5},
                {"keyword": "房产APP", "weight": 5},
                {"keyword": "楼盘开盘", "weight": 5},
                {"keyword": "购房优惠", "weight": 5},
                {"keyword": "房产中介", "weight": 5},
                {"keyword": "客户画像", "weight": 4},
                {"keyword": "房源定价", "weight": 4},
                {"keyword": "房产税费", "weight": 4},
                {"keyword": "购房合同", "weight": 4},
                {"keyword": "楼盘活动", "weight": 4},
                {"keyword": "房产销售培训", "weight": 3},
                {"keyword": "客户回访", "weight": 3},
                {"keyword": "房源信息维护", "weight": 3},
                {"keyword": "房产销售话术", "weight": 3},
                {"keyword": "楼盘推广", "weight": 3},
                {"keyword": "购房贷款流程", "weight": 3},
                {"keyword": "客户签约跟进", "weight": 3},
                {"keyword": "房产市场趋势", "weight": 3},
                {"keyword": "房源户型", "weight": 3},
                {"keyword": "购房首付", "weight": 3},
                {"keyword": "楼盘交付", "weight": 3},
                {"keyword": "房产销售复盘", "weight": 3},
                {"keyword": "客户购房意向", "weight": 3},
                {"keyword": "房源面积", "weight": 3},
                {"keyword": "房产中介合作", "weight": 3},
                {"keyword": "购房按揭", "weight": 3}
            ]
        },
        "metrics_examples": ["年销售额5000万+", "成交客户50+人"],
        "suitable_for": ["本科应届", "有经验"]
    }
}

# 更新现有行业关键词
for industry, expansion in keyword_expansions.items():
    if industry in data:
        data[industry]["keywords"] = expansion

# 添加新行业
for industry, info in new_industries.items():
    data[industry] = info

# 保存更新后的关键词库
with open('keywords.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"关键词库扩展完成")
print(f"总行业数: {len(data)}")
for ind in ["sales", "finance", "administrative"]:
    kw_count = len(data[ind]["keywords"]["required"]) + len(data[ind]["keywords"]["preferred"])
    print(f"  {ind}: {kw_count}个关键词")
print()
print("新增行业:")
for ind, info in new_industries.items():
    kw_count = len(info["keywords"]["required"]) + len(info["keywords"]["preferred"])
    print(f"  {info['name']} ({ind}): {kw_count}个关键词")