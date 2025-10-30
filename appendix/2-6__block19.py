import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# 创建模拟数据质量修复场景
def create_repair_scenario():
    np.random.seed(42)
    
    # 1. 生成修复前后的数据质量指标
    quality_metrics = ['完整性', '准确性', '一致性', '时效性', '可靠性']
    
    # 创建修复前指标
    pre_repair = {}
    for metric in quality_metrics:
        # 生成60%-85%之间的初始质量分数
        pre_repair[metric] = round(np.random.uniform(60, 85), 2)
    
    # 创建修复后指标
    post_repair = {}
    improvement_potential = {'完整性': 20, '准确性': 15, '一致性': 25, '时效性': 18, '可靠性': 12}
    
    for metric in quality_metrics:
        # 基于修复前分数和改进潜力生成修复后分数
        max_possible = min(100, pre_repair[metric] + improvement_potential[metric])
        post_repair[metric] = round(np.random.uniform(pre_repair[metric] + 5, max_possible), 2)
    
    # 2. 生成修复成本数据
    costs = {
        '人力成本': round(np.random.uniform(50000, 150000), 2),
        '技术成本': round(np.random.uniform(20000, 80000), 2),
        '时间成本': round(np.random.uniform(10000, 30000), 2),
        '其他成本': round(np.random.uniform(5000, 20000), 2)
    }
    
    # 3. 生成业务收益数据
    benefits = {
        '减少运营错误成本': round(np.random.uniform(80000, 200000), 2),
        '提高决策效率价值': round(np.random.uniform(60000, 150000), 2),
        '提升客户满意度价值': round(np.random.uniform(40000, 120000), 2),
        '避免数据丢失风险价值': round(np.random.uniform(50000, 180000), 2)
    }
    
    # 4. 生成长期效果跟踪数据（12个月）
    months = pd.date_range(start='2023-01-01', periods=12, freq='M')
    long_term_data = []
    
    for metric in quality_metrics:
        # 基于修复后分数生成长期数据，加入一些随机波动
        base_value = post_repair[metric]
        
        for i, month in enumerate(months):
            # 添加一些随机波动，但保持整体趋势稳定
            fluctuation = np.random.normal(0, 1.5)
            # 前几个月可能有小幅上升，之后趋于稳定
            if i < 3:
                trend = 0.5  # 小幅上升趋势
            else:
                trend = 0  # 趋于稳定
            
            value = base_value + fluctuation + trend
            # 确保值在合理范围内
            value = max(70, min(100, value))
            
            long_term_data.append({
                '日期': month,
                '指标': metric,
                '分数': round(value, 2)
            })
    
    long_term_df = pd.DataFrame(long_term_data)
    
    # 5. 生成案例研究数据
    case_study = {
        '项目名称': '客户数据质量提升项目',
        '问题描述': '客户数据库存在大量缺失值、重复记录和格式不一致问题，影响营销效果和客户服务质量',
        '修复策略': '采用预防性修复+自动修复+批量修复的组合策略',
        '实施周期': '8周',
        '参与团队': '数据管理团队、IT支持团队、业务分析师',
        '主要挑战': '历史数据量大、业务规则复杂、系统集成困难',
        '解决方案': '分阶段实施、自动化工具应用、跨部门协作',
        '经验教训': '早期业务参与、明确的数据标准、持续监控机制',
        '最佳实践': '建立数据治理委员会、实施主数据管理、定期数据质量审计'
    }
    
    return {
        'pre_repair': pre_repair,
        'post_repair': post_repair,
        'costs': costs,
        'benefits': benefits,
        'long_term_data': long_term_df,
        'case_study': case_study
    }

# 修复验证与评估函数
def validate_and_evaluate_repair(scenario):
    print("=== 数据质量修复验证与评估报告 ===\n")
    
    # 1. 修复后验证
    print("1. 修复后验证结果:")
    pre_repair = scenario['pre_repair']
    post_repair = scenario['post_repair']
    
    print("   数据质量指标对比:")
    print(f"   {'指标':<8} {'修复前':<8} {'修复后':<8} {'改进幅度':<8} {'状态':<8}")
    print("   " + "-" * 48)
    
    validation_results = {}
    for metric in pre_repair.keys():
        improvement = post_repair[metric] - pre_repair[metric]
        improvement_pct = (improvement / pre_repair[metric]) * 100
        
        # 验证状态判断
        if post_repair[metric] >= 95:
            status = "优秀"
        elif post_repair[metric] >= 90:
            status = "良好"
        elif post_repair[metric] >= 85:
            status = "可接受"
        else:
            status = "需改进"
        
        validation_results[metric] = {
            'pre_repair': pre_repair[metric],
            'post_repair': post_repair[metric],
            'improvement': improvement,
            'improvement_pct': improvement_pct,
            'status': status
        }
        
        print(f"   {metric:<8} {pre_repair[metric]:<8.2f} {post_repair[metric]:<8.2f} {improvement_pct:<8.2f}% {status:<8}")
    
    # 2. 质量提升评估
    print("\n2. 质量提升评估:")
    
    # 计算整体质量提升
    avg_pre_quality = sum(pre_repair.values()) / len(pre_repair)
    avg_post_quality = sum(post_repair.values()) / len(post_repair)
    avg_improvement = avg_post_quality - avg_pre_quality
    avg_improvement_pct = (avg_improvement / avg_pre_quality) * 100
    
    print(f"   整体数据质量平均分数: {avg_pre_quality:.2f} → {avg_post_quality:.2f}")
    print(f"   整体提升幅度: {avg_improvement:.2f} 分 ({avg_improvement_pct:.2f}%)")
    
    # 找出改进最显著的指标
    max_improvement_metric = max(validation_results.keys(), 
                                key=lambda x: validation_results[x]['improvement_pct'])
    print(f"   改进最显著的指标: {max_improvement_metric} (提升 {validation_results[max_improvement_metric]['improvement_pct']:.2f}%)")
    
    # 3. 修复成本分析
    print("\n3. 修复成本分析:")
    costs = scenario['costs']
    total_cost = sum(costs.values())
    
    print(f"   修复成本明细:")
    for cost_type, amount in costs.items():
        percentage = (amount / total_cost) * 100
        print(f"   - {cost_type}: {amount:,.2f} ({percentage:.2f}%)")
    print(f"   总成本: {total_cost:,.2f}")
    
    # 4. ROI计算
    print("\n4. 投资回报率(ROI)计算:")
    benefits = scenario['benefits']
    total_benefit = sum(benefits.values())
    roi = ((total_benefit - total_cost) / total_cost) * 100
    payback_period = total_cost / (total_benefit / 12)  # 假设收益按月均分布
    
    print(f"   预期收益明细:")
    for benefit_type, amount in benefits.items():
        percentage = (amount / total_benefit) * 100
        print(f"   - {benefit_type}: {amount:,.2f} ({percentage:.2f}%)")
    
    print(f"   总收益: {total_benefit:,.2f}")
    print(f"   投资回报率(ROI): {roi:.2f}%")
    print(f"   预计回收期: {payback_period:.1f} 个月")
    
    # 5. 长期效果分析
    print("\n5. 长期效果分析:")
    long_term_df = scenario['long_term_data']
    
    # 计算每个指标的平均值和趋势
    metric_performance = {}
    for metric in pre_repair.keys():
        metric_data = long_term_df[long_term_df['指标'] == metric]
        avg_performance = metric_data['分数'].mean()
        # 计算趋势（最后一个月与第一个月的差值）
        trend = metric_data['分数'].iloc[-1] - metric_data['分数'].iloc[0]
        
        metric_performance[metric] = {
            'avg_performance': avg_performance,
            'trend': trend,
            'consistency': metric_data['分数'].std()  # 用标准差衡量一致性
        }
        
        trend_dir = "上升" if trend > 0 else "下降" if trend < 0 else "稳定"
        print(f"   - {metric}: 平均分数={avg_performance:.2f}, 趋势={trend_dir} ({abs(trend):.2f}分), 稳定性={metric_data['分数'].std():.2f}")
    
    # 6. 案例研究总结
    print("\n6. 案例研究总结:")
    case_study = scenario['case_study']
    
    print(f"   项目名称: {case_study['项目名称']}")
    print(f"   问题描述: {case_study['问题描述']}")
    print(f"   修复策略: {case_study['修复策略']}")
    print(f"   实施周期: {case_study['实施周期']}")
    print(f"   主要挑战: {case_study['主要挑战']}")
    print(f"   解决方案: {case_study['解决方案']}")
    
    print("\n7. 经验教训与最佳实践:")
    print(f"   经验教训: {case_study['经验教训']}")
    print(f"   最佳实践: {case_study['最佳实践']}")
    
    # 8. 总体评估与建议
    print("\n8. 总体评估与建议:")
    
    # 基于各项指标的总体评估
    if avg_post_quality >= 90 and roi > 100:
        overall_assessment = "优秀"
    elif avg_post_quality >= 85 and roi > 50:
        overall_assessment = "良好"
    else:
        overall_assessment = "需改进"
    
    print(f"   总体评估: {overall_assessment}")
    
    # 提出改进建议
    print("   改进建议:")
    
    # 基于验证状态提出建议
    for metric, result in validation_results.items():
        if result['status'] != "优秀":
            print(f"   - {metric}指标仍有提升空间，当前得分为{result['post_repair']:.2f}，建议进一步优化相关流程")
    
    # 基于长期趋势提出建议
    for metric, perf in metric_performance.items():
        if perf['trend'] < -2:  # 如果趋势下降超过2分
            print(f"   - {metric}指标出现下降趋势，建议加强监控并分析原因")
        elif perf['consistency'] > 3:  # 如果波动较大
            print(f"   - {metric}指标波动较大，建议建立更稳定的数据管理流程")
    
    print("   - 建议建立持续的数据质量监控机制")
    print("   - 定期进行数据质量审计和评估")
    print("   - 将数据质量指标纳入绩效考核体系")
    
    return {
        'validation_results': validation_results,
        'quality_improvement': {
            'avg_pre_quality': avg_pre_quality,
            'avg_post_quality': avg_post_quality,
            'avg_improvement_pct': avg_improvement_pct
        },
        'cost_analysis': {
            'total_cost': total_cost,
            'cost_breakdown': costs
        },
        'roi_analysis': {
            'total_benefit': total_benefit,
            'roi': roi,
            'payback_period': payback_period
        },
        'long_term_performance': metric_performance,
        'overall_assessment': overall_assessment
    }

# 运行修复验证与评估示例
scenario = create_repair_scenario()
evaluation_results = validate_and_evaluate_repair(scenario)
