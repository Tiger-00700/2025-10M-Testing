import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 创建数据质量问题模拟系统
def create_data_quality_system():
    # 生成不同类型的数据质量问题
    np.random.seed(42)
    
    # 问题类型和严重性
    issue_types = ["缺失数据", "错误数据", "重复数据", "不一致数据", "过时数据", "格式错误"]
    severity_levels = ["低", "中", "高", "严重"]
    
    # 生成模拟数据质量问题
    n_issues = 20
    issues = []
    
    for i in range(1, n_issues + 1):
        issue_type = random.choice(issue_types)
        severity = random.choice(severity_levels)
        
        # 根据问题类型生成更具体的描述
        if issue_type == "缺失数据":
            details = random.choice([
                "客户表中邮箱地址字段缺失率达15%",
                "交易记录中产品类别代码缺失",
                "员工信息表中联系方式缺失"
            ])
        elif issue_type == "错误数据":
            details = random.choice([
                "产品价格包含负值",
                "客户年龄超过150岁",
                "交易日期晚于当前日期"
            ])
        elif issue_type == "重复数据":
            details = random.choice([
                "客户表中存在多个重复记录",
                "产品目录中同一产品出现多次",
                "交易系统中存在重复订单"
            ])
        elif issue_type == "不一致数据":
            details = random.choice([
                "销售系统与财务系统中的客户名称不一致",
                "主数据管理系统与业务系统中的产品信息不同步",
                "不同区域的销售报表数据不一致"
            ])
        elif issue_type == "过时数据":
            details = random.choice([
                "客户地址信息未更新超过2年",
                "产品价格信息过时",
                "员工职位信息未反映最新变动"
            ])
        else:  # 格式错误
            details = random.choice([
                "日期格式不统一，同时存在多种格式",
                "电话号码格式混乱",
                "邮政编码格式不符合标准"
            ])
        
        # 生成发现日期和影响范围
        days_ago = random.randint(1, 90)
        discovery_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # 模拟影响的记录数和业务领域
        affected_records = random.randint(10, 10000)
        business_domain = random.choice(["销售", "客户服务", "财务", "物流", "人力资源"])
        
        # 计算业务影响分数（1-10分）
        severity_score = {"低": 1, "中": 3, "高": 7, "严重": 10}[severity]
        impact_score = min(10, severity_score * (1 + min(affected_records / 1000, 1)))
        
        issues.append({
            "问题ID": f"DQ-{i:03d}",
            "问题类型": issue_type,
            "严重程度": severity,
            "详细描述": details,
            "发现日期": discovery_date,
            "影响记录数": affected_records,
            "业务领域": business_domain,
            "业务影响分数": round(impact_score, 2)
        })
    
    return pd.DataFrame(issues)

# 修复策略选择函数
def select_repair_strategy(issues_df):
    print("=== 数据质量问题修复策略选择报告 ===\n")
    
    # 创建结果DataFrame
    results = issues_df.copy()
    results['推荐修复策略'] = ''
    results['修复策略说明'] = ''
    results['预期工作量'] = ''
    results['优先级'] = ''
    
    # 定义修复策略选择逻辑
    for idx, issue in results.iterrows():
        # 1. 优先级确定（基于业务影响分数和严重程度）
        impact_score = issue['业务影响分数']
        if impact_score >= 8:
            priority = "紧急"
        elif impact_score >= 5:
            priority = "高"
        elif impact_score >= 3:
            priority = "中"
        else:
            priority = "低"
        
        # 2. 基于问题类型和特性选择修复策略
        issue_type = issue['问题类型']
        affected_records = issue['影响记录数']
        
        # 策略组合逻辑
        strategies = []
        strategy_details = []
        
        # 预防性修复判断
        if issue_type in ["错误数据", "格式错误"] or (issue_type == "缺失数据" and priority in ["紧急", "高"]):
            strategies.append("预防性修复")
            strategy_details.append("实施数据录入验证、格式检查和业务规则约束，防止类似问题再次发生")
        
        # 自动修复判断
        if issue_type in ["重复数据", "格式错误"] or (issue_type == "缺失数据" and priority in ["紧急", "高"]):
            strategies.append("自动修复")
            if issue_type == "重复数据":
                strategy_details.append("开发自动化脚本识别并合并重复记录")
            elif issue_type == "格式错误":
                strategy_details.append("使用数据转换工具标准化数据格式")
            else:  # 缺失数据
                strategy_details.append("利用业务规则和统计方法自动填充缺失值")
        
        # 手动修复判断
        if issue_type in ["不一致数据", "错误数据"] and priority in ["紧急", "高"]:
            strategies.append("手动修复")
            strategy_details.append("组织业务专家审核并修复关键数据，确保业务逻辑一致性")
        
        # 批量修复判断
        if affected_records > 1000 or (issue_type in ["过时数据", "重复数据"] and priority in ["高", "中"]):
            strategies.append("批量修复")
            strategy_details.append("执行大规模数据清洗作业，一次性处理大量数据问题")
        
        # 增量修复判断
        if priority == "低" or (affected_records > 5000 and priority == "中"):
            strategies.append("增量修复")
            strategy_details.append("制定分期修复计划，优先处理高价值数据，逐步改进整体数据质量")
        
        # 被动性修复作为兜底
        if not strategies:
            strategies.append("被动性修复")
            strategy_details.append("在数据使用过程中发现问题时进行修复")
        
        # 3. 估计工作量
        if len(strategies) <= 1:
            workload = "小"
        elif len(strategies) == 2:
            workload = "中"
        else:
            workload = "大"
        
        # 调整工作量（根据影响记录数）
        if affected_records > 5000:
            if workload == "小":
                workload = "中"
            elif workload == "中":
                workload = "大"
        
        # 更新结果
        results.at[idx, '推荐修复策略'] = " + ".join(strategies)
        results.at[idx, '修复策略说明'] = "\n".join([f"- {detail}" for detail in strategy_details])
        results.at[idx, '预期工作量'] = workload
        results.at[idx, '优先级'] = priority
    
    # 按优先级和业务影响分数排序
    priority_order = {'紧急': 0, '高': 1, '中': 2, '低': 3}
    results['优先级排序'] = results['优先级'].map(priority_order)
    results = results.sort_values(['优先级排序', '业务影响分数'], ascending=[True, False])
    results.drop('优先级排序', axis=1, inplace=True)
    
    # 输出摘要报告
    print(f"共发现 {len(results)} 个数据质量问题")
    print(f"\n按优先级分布:")
    print(results['优先级'].value_counts())
    print(f"\n按问题类型分布:")
    print(results['问题类型'].value_counts())
    print(f"\n按业务领域分布:")
    print(results['业务领域'].value_counts())
    
    # 输出前几个高优先级问题的详细修复策略
    high_priority_issues = results[results['优先级'].isin(['紧急', '高'])]
    if not high_priority_issues.empty:
        print(f"\n=== 高优先级问题修复策略详情 ===")
        for idx, issue in high_priority_issues.head().iterrows():
            print(f"\n问题ID: {issue['问题ID']}")
            print(f"问题类型: {issue['问题类型']}")
            print(f"严重程度: {issue['严重程度']}")
            print(f"详细描述: {issue['详细描述']}")
            print(f"业务影响分数: {issue['业务影响分数']}")
            print(f"影响记录数: {issue['影响记录数']}")
            print(f"业务领域: {issue['业务领域']}")
            print(f"推荐修复策略: {issue['推荐修复策略']}")
            print(f"修复策略说明:")
            print(issue['修复策略说明'])
            print(f"预期工作量: {issue['预期工作量']}")
    
    # 生成修复计划建议
    print(f"\n=== 整体修复计划建议 ===")
    
    # 计算各优先级问题数量
    priority_counts = results['优先级'].value_counts()
    
    # 估算时间线（基于优先级和工作量）
    print(f"\n1. 紧急优先级问题 ({priority_counts.get('紧急', 0)}个):")
    print("   - 建议立即启动修复，目标在1-2周内完成")
    print("   - 组建专项团队，优先实施自动修复和手动修复相结合的策略")
    
    print(f"\n2. 高优先级问题 ({priority_counts.get('高', 0)}个):")
    print("   - 建议在1个月内完成修复")
    print("   - 根据问题类型组合使用预防性修复、自动修复和手动修复")
    
    print(f"\n3. 中优先级问题 ({priority_counts.get('中', 0)}个):")
    print("   - 建议在3个月内制定并执行修复计划")
    print("   - 主要采用批量修复和自动修复策略")
    
    print(f"\n4. 低优先级问题 ({priority_counts.get('低', 0)}个):")
    print("   - 建议采用增量修复策略，纳入日常数据维护工作")
    print("   - 可以与系统升级或其他数据项目结合进行")
    
    print(f"\n5. 长期策略建议:")
    print("   - 建立数据质量监控体系，提前发现和预防问题")
    print("   - 制定数据质量标准和操作规范")
    print("   - 定期进行数据质量评估和审计")
    print("   - 培训相关人员，提高数据质量意识和技能")
    
    return results

# 运行修复策略选择示例
issues_df = create_data_quality_system()
strategy_results = select_repair_strategy(issues_df)
