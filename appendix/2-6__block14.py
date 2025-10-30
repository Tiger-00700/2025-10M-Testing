# 数据质量持续改进框架示例
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class DataQualityImprovementFramework:
    """数据质量持续改进框架"""
    
    def __init__(self):
        self.issue_registry = {}  # 问题注册表
        self.root_cause_analysis = {}  # 根因分析记录
        self.action_items = []  # 改进措施项
        self.practice_library = []  # 最佳实践库
        self.improvement_metrics = defaultdict(list)  # 改进指标跟踪
        self.issue_counter = 0  # 问题计数器
    
    def register_issue(self, issue_title, data_domain, severity, description, impact_areas):
        """注册数据质量问题
        
        参数:
        issue_title: 问题标题
        data_domain: 数据域
        severity: 严重程度 (critical, high, medium, low)
        description: 问题描述
        impact_areas: 影响区域列表
        
        返回:
        问题ID
        """
        self.issue_counter += 1
        issue_id = f"DQI-{self.issue_counter}"
        
        issue = {
            'issue_id': issue_id,
            'title': issue_title,
            'data_domain': data_domain,
            'severity': severity,
            'description': description,
            'impact_areas': impact_areas,
            'registration_date': datetime.now(),
            'status': 'open',
            'resolution_date': None,
            'resolved_by': None
        }
        
        self.issue_registry[issue_id] = issue
        print(f"已注册问题: {issue_id} - {issue_title}")
        return issue_id
    
    def perform_root_cause_analysis(self, issue_id, analysis_method, potential_causes, confirmed_cause, contributing_factors):
        """执行根因分析
        
        参数:
        issue_id: 问题ID
        analysis_method: 分析方法
        potential_causes: 潜在原因列表
        confirmed_cause: 确认的根本原因
        contributing_factors: 促成因素列表
        """
        if issue_id not in self.issue_registry:
            print(f"错误: 问题 {issue_id} 不存在")
            return None
        
        analysis = {
            'analysis_id': f"RCA-{issue_id}",
            'issue_id': issue_id,
            'analysis_date': datetime.now(),
            'analysis_method': analysis_method,
            'potential_causes': potential_causes,
            'confirmed_cause': confirmed_cause,
            'contributing_factors': contributing_factors,
            'recommended_actions': []
        }
        
        self.root_cause_analysis[issue_id] = analysis
        
        # 更新问题状态
        self.issue_registry[issue_id]['status'] = 'analyzed'
        
        print(f"已完成问题 {issue_id} 的根因分析")
        return analysis
    
    def create_action_item(self, issue_id, action_description, responsible_team, target_completion_date, priority):
        """创建改进措施项
        
        参数:
        issue_id: 问题ID
        action_description: 措施描述
        responsible_team: 负责团队
        target_completion_date: 目标完成日期
        priority: 优先级 (high, medium, low)
        
        返回:
        措施ID
        """
        if issue_id not in self.issue_registry:
            print(f"错误: 问题 {issue_id} 不存在")
            return None
        
        action_id = f"ACTION-{len(self.action_items) + 1}"
        action_item = {
            'action_id': action_id,
            'issue_id': issue_id,
            'description': action_description,
            'responsible_team': responsible_team,
            'creation_date': datetime.now(),
            'target_completion_date': target_completion_date,
            'actual_completion_date': None,
            'priority': priority,
            'status': 'planned',  # planned, in_progress, completed, blocked
            'outcome': None,
            'lessons_learned': None
        }
        
        self.action_items.append(action_item)
        
        # 更新根因分析中的推荐措施
        if issue_id in self.root_cause_analysis:
            self.root_cause_analysis[issue_id]['recommended_actions'].append(action_id)
        
        print(f"已创建改进措施: {action_id} - {action_description}")
        return action_id
    
    def update_action_status(self, action_id, status, outcome=None, lessons_learned=None):
        """更新措施状态
        
        参数:
        action_id: 措施ID
        status: 新状态
        outcome: 措施结果（可选）
        lessons_learned: 经验教训（可选）
        """
        for action in self.action_items:
            if action['action_id'] == action_id:
                action['status'] = status
                
                if status == 'completed':
                    action['actual_completion_date'] = datetime.now()
                    action['outcome'] = outcome
                    action['lessons_learned'] = lessons_learned
                
                print(f"已更新措施 {action_id} 的状态为: {status}")
                return True
        
        print(f"错误: 措施 {action_id} 不存在")
        return False
    
    def resolve_issue(self, issue_id, resolution_description, resolved_by):
        """解决问题
        
        参数:
        issue_id: 问题ID
        resolution_description: 解决方案描述
        resolved_by: 解决人
        """
        if issue_id not in self.issue_registry:
            print(f"错误: 问题 {issue_id} 不存在")
            return False
        
        issue = self.issue_registry[issue_id]
        issue['status'] = 'resolved'
        issue['resolution_date'] = datetime.now()
        issue['resolved_by'] = resolved_by
        issue['resolution_description'] = resolution_description
        
        print(f"已解决问题: {issue_id} - {issue['title']}")
        return True
    
    def document_best_practice(self, practice_title, data_domain, issue_type, solution_approach, effectiveness_metrics):
        """记录最佳实践
        
        参数:
        practice_title: 实践标题
        data_domain: 数据域
        issue_type: 问题类型
        solution_approach: 解决方案方法
        effectiveness_metrics: 有效性指标
        
        返回:
        实践ID
        """
        practice_id = f"BP-{len(self.practice_library) + 1}"
        practice = {
            'practice_id': practice_id,
            'title': practice_title,
            'data_domain': data_domain,
            'issue_type': issue_type,
            'solution_approach': solution_approach,
            'effectiveness_metrics': effectiveness_metrics,
            'documentation_date': datetime.now(),
            'last_updated': datetime.now(),
            'usage_count': 0
        }
        
        self.practice_library.append(practice)
        print(f"已记录最佳实践: {practice_id} - {practice_title}")
        return practice_id
    
    def track_improvement_metric(self, metric_name, metric_value, timestamp=None):
        """跟踪改进指标
        
        参数:
        metric_name: 指标名称
        metric_value: 指标值
        timestamp: 时间戳（可选）
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        self.improvement_metrics[metric_name].append({
            'timestamp': timestamp,
            'value': metric_value
        })
    
    def generate_improvement_report(self, time_period=None):
        """生成改进报告
        
        参数:
        time_period: 时间周期（天数）
        
        返回:
        改进报告
        """
        report = {
            'report_date': datetime.now(),
            'issue_summary': {},
            'action_summary': {},
            'practice_summary': {},
            'improvement_trends': {},
            'recommendations': []
        }
        
        # 问题统计
        issue_counts = Counter()
        severity_counts = Counter()
        status_counts = Counter()
        
        for issue in self.issue_registry.values():
            # 如果指定了时间范围，只统计该范围内的问题
            if time_period:
                cutoff_date = datetime.now() - timedelta(days=time_period)
                if issue['registration_date'] < cutoff_date:
                    continue
            
            issue_counts[issue['data_domain']] += 1
            severity_counts[issue['severity']] += 1
            status_counts[issue['status']] += 1
        
        report['issue_summary'] = {
            'total_issues': sum(issue_counts.values()),
            'by_domain': dict(issue_counts),
            'by_severity': dict(severity_counts),
            'by_status': dict(status_counts)
        }
        
        # 措施统计
        action_status_counts = Counter()
        priority_counts = Counter()
        overdue_count = 0
        
        today = datetime.now()
        for action in self.action_items:
            action_status_counts[action['status']] += 1
            priority_counts[action['priority']] += 1
            
            if action['status'] != 'completed' and action['target_completion_date'] < today:
                overdue_count += 1
        
        report['action_summary'] = {
            'total_actions': len(self.action_items),
            'by_status': dict(action_status_counts),
            'by_priority': dict(priority_counts),
            'overdue_actions': overdue_count
        }
        
        # 最佳实践统计
        report['practice_summary'] = {
            'total_practices': len(self.practice_library),
            'recent_practices': [p for p in self.practice_library 
                               if (datetime.now() - p['documentation_date']).days <= 90]
        }
        
        # 改进趋势
        for metric_name, metric_data in self.improvement_metrics.items():
            # 按时间排序
            sorted_data = sorted(metric_data, key=lambda x: x['timestamp'])
            
            # 提取时间序列数据
            timestamps = [d['timestamp'] for d in sorted_data]
            values = [d['value'] for d in sorted_data]
            
            if len(values) >= 2:
                # 计算总体改进百分比
                overall_improvement = ((values[-1] - values[0]) / values[0]) * 100
                
                report['improvement_trends'][metric_name] = {
                    'data_points': list(zip(timestamps, values)),
                    'current_value': values[-1],
                    'baseline_value': values[0],
                    'overall_improvement_percent': overall_improvement,
                    'trend': 'improving' if values[-1] > values[0] else 'declining' if values[-1] < values[0] else 'stable'
                }
        
        # 生成建议
        if status_counts.get('open', 0) > 5:
            report['recommendations'].append("优先处理积压的开放问题，特别是高严重性的问题")
        
        if overdue_count > 3:
            report['recommendations'].append("关注逾期的改进措施，与负责团队沟通并提供支持")
        
        if len(self.practice_library) < 5:
            report['recommendations'].append("加强最佳实践的收集和记录，建立更完善的知识库")
        
        return report

# 示例：使用持续改进框架
def continuous_improvement_example():
    # 初始化改进框架
    framework = DataQualityImprovementFramework()
    
    # 1. 注册数据质量问题
    issue_id1 = framework.register_issue(
        "客户地址数据不一致",
        "CRM系统",
        "high",
        "客户地址在CRM系统和订单系统中存在不一致的情况",
        ["客户分析", "订单处理", "配送服务"]
    )
    
    issue_id2 = framework.register_issue(
        "交易数据缺失",
        "销售系统",
        "critical",
        "部分交易记录的金额字段缺失",
        ["财务报表", "销售分析", "收入确认"]
    )
    
    # 2. 执行根因分析
    framework.perform_root_cause_analysis(
        issue_id1,
        "5-Why分析法",
        ["数据同步机制失效", "手动更新绕过验证", "系统集成接口故障"],
        "数据同步机制失效，导致CRM系统的更新未同步到订单系统",
        ["缺乏数据质量监控", "同步作业未设置告警", "数据验证规则不完整"]
    )
    
    framework.perform_root_cause_analysis(
        issue_id2,
        "鱼骨图分析",
        ["数据录入错误", "系统故障", "业务流程缺陷"],
        "业务流程缺陷，部分交易未经过完整的数据验证环节",
        ["员工培训不足", "系统提示不明确", "缺乏强制性验证"]
    )
    
    # 3. 创建改进措施
    action_id1 = framework.create_action_item(
        issue_id1,
        "修复数据同步机制，实现双向实时同步",
        "数据集成团队",
        datetime.now() + timedelta(days=14),
        "high"
    )
    
    action_id2 = framework.create_action_item(
        issue_id1,
        "实施数据验证规则，确保地址数据格式一致性",
        "数据质量团队",
        datetime.now() + timedelta(days=7),
        "high"
    )
    
    action_id3 = framework.create_action_item(
        issue_id2,
        "修改业务流程，增加交易数据强制性验证环节",
        "业务流程团队",
        datetime.now() + timedelta(days=10),
        "high"
    )
    
    action_id4 = framework.create_action_item(
        issue_id2,
        "对现有缺失数据进行修复和补充",
        "数据修复团队",
        datetime.now() + timedelta(days=5),
        "high"
    )
    
    # 4. 更新措施状态
    framework.update_action_status(
        action_id2,
        "completed",
        "成功实施了地址格式验证规则，一致性提升至99.5%",
        "在实施过程中发现现有地址数据存在多种格式，需要制定统一的标准化方案"
    )
    
    framework.update_action_status(
        action_id4,
        "completed",
        "已修复98%的缺失交易数据，剩余2%因信息不足无法修复",
        "建议建立数据恢复机制，确保系统故障时数据不丢失"
    )
    
    framework.update_action_status(action_id1, "in_progress")
    framework.update_action_status(action_id3, "in_progress")
    
    # 5. 解决问题
    framework.resolve_issue(
        issue_id2,
        "通过修复流程和补充数据，解决了交易数据缺失问题",
        "数据质量管理团队"
    )
    
    # 6. 记录最佳实践
    framework.document_best_practice(
        "交易数据完整性保障流程",
        "销售系统",
        "数据缺失",
        "实施多阶段数据验证，包括前置检查、实时验证和事后审计",
        {"数据完整性提升": "95%", "问题发现提前量": "平均提前48小时"}
    )
    
    # 7. 跟踪改进指标
    # 模拟一段时间内的数据质量指标变化
    for i in range(12):
        date = datetime.now() - timedelta(days=30-i*2.5)
        framework.track_improvement_metric("data_completeness", 85 + i*1.2, date)
        framework.track_improvement_metric("data_consistency", 88 + i*0.8, date)
        framework.track_improvement_metric("data_accuracy", 90 + i*0.5, date)
    
    # 8. 生成改进报告
    report = framework.generate_improvement_report()
    
    # 输出报告摘要
    print("\n=== 数据质量持续改进报告 ===")
    print(f"报告生成时间: {report['report_date']}")
    
    print(f"\n问题统计:")
    print(f"  总问题数: {report['issue_summary']['total_issues']}")
    print(f"  按状态分布: {report['issue_summary']['by_status']}")
    print(f"  按严重程度分布: {report['issue_summary']['by_severity']}")
    
    print(f"\n改进措施统计:")
    print(f"  总措施数: {report['action_summary']['total_actions']}")
    print(f"  按状态分布: {report['action_summary']['by_status']}")
    print(f"  逾期措施数: {report['action_summary']['overdue_actions']}")
    
    print(f"\n最佳实践统计:")
    print(f"  总实践数: {report['practice_summary']['total_practices']}")
    print(f"  近期新增实践: {len(report['practice_summary']['recent_practices'])}")
    
    print(f"\n改进趋势:")
    for metric, trend in report['improvement_trends'].items():
        print(f"  {metric}: 当前值={trend['current_value']:.2f}, "
              f"基线值={trend['baseline_value']:.2f}, "
              f"改进={trend['overall_improvement_percent']:+.2f}%, "
              f"趋势={trend['trend']}")
    
    print(f"\n建议:")
    for i, recommendation in enumerate(report['recommendations'], 1):
        print(f"  {i}. {recommendation}")

# 运行持续改进示例
continuous_improvement_example()
