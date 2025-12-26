"""
流程评估与基线建立 (Process Assessment and Baseline Establishment)

此脚本用于评估软件开发流程的当前状态，建立性能基线，并识别改进机会。
基于敏捷和DevOps最佳实践，提供流程成熟度评估和基线指标计算。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import json


class ProcessMaturityLevel(Enum):
    INITIAL = 1      # 初始级：流程无序，依赖个人
    REPEATABLE = 2   # 可重复级：基本流程建立
    DEFINED = 3      # 已定义级：标准化流程
    MANAGED = 4      # 受控级：量化管理和监控
    OPTIMIZING = 5   # 优化级：持续改进和创新


@dataclass
class ProcessMetrics:
    """流程指标数据类"""
    cycle_time_days: float  # 周期时间（天）
    defect_density: float   # 缺陷密度（每千行代码）
    throughput_velocity: float  # 吞吐量（故事点/周）
    quality_gate_pass_rate: float  # 质量门通过率（%）
    team_velocity_stability: float  # 团队速度稳定性（%）


@dataclass
class ProcessAssessment:
    """流程评估结果"""
    current_maturity: ProcessMaturityLevel
    metrics: ProcessMetrics
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    baseline_score: float  # 基线得分（0-100）


class ProcessAssessmentEngine:
    """流程评估引擎"""

    def __init__(self):
        self.maturity_thresholds = {
            ProcessMaturityLevel.INITIAL: 20,
            ProcessMaturityLevel.REPEATABLE: 40,
            ProcessMaturityLevel.DEFINED: 60,
            ProcessMaturityLevel.MANAGED: 80,
            ProcessMaturityLevel.OPTIMIZING: 95
        }

    def assess_process(self, metrics: ProcessMetrics) -> ProcessAssessment:
        """评估流程成熟度"""
        # 计算综合得分
        score = self._calculate_overall_score(metrics)

        # 确定成熟度等级
        maturity = self._determine_maturity_level(score)

        # 生成分析结果
        strengths = self._identify_strengths(metrics)
        weaknesses = self._identify_weaknesses(metrics)
        recommendations = self._generate_recommendations(metrics, maturity)

        return ProcessAssessment(
            current_maturity=maturity,
            metrics=metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            baseline_score=score
        )

    def _calculate_overall_score(self, metrics: ProcessMetrics) -> float:
        """计算综合得分"""
        # 标准化指标计算
        cycle_time_score = max(0, 100 - (metrics.cycle_time_days - 7) * 5)  # 7天为基准
        defect_score = max(0, 100 - metrics.defect_density * 10)  # 10缺陷/千行为基准
        throughput_score = min(100, metrics.throughput_velocity * 2)  # 50故事点/周为满分
        quality_score = metrics.quality_gate_pass_rate
        stability_score = metrics.team_velocity_stability

        # 加权平均
        weights = [0.2, 0.25, 0.2, 0.2, 0.15]
        scores = [cycle_time_score, defect_score, throughput_score, quality_score, stability_score]

        return sum(w * s for w, s in zip(weights, scores))

    def _determine_maturity_level(self, score: float) -> ProcessMaturityLevel:
        """确定成熟度等级"""
        for level, threshold in sorted(self.maturity_thresholds.items(), reverse=True):
            if score >= threshold:
                return level
        return ProcessMaturityLevel.INITIAL

    def _identify_strengths(self, metrics: ProcessMetrics) -> List[str]:
        """识别优势"""
        strengths = []
        if metrics.quality_gate_pass_rate > 90:
            strengths.append("高质量门控机制完善")
        if metrics.team_velocity_stability > 80:
            strengths.append("团队交付稳定性高")
        if metrics.throughput_velocity > 30:
            strengths.append("开发效率较高")
        if metrics.defect_density < 5:
            strengths.append("代码质量优秀")
        if metrics.cycle_time_days < 14:
            strengths.append("交付周期较短")
        return strengths or ["需要进一步评估具体优势"]

    def _identify_weaknesses(self, metrics: ProcessMetrics) -> List[str]:
        """识别劣势"""
        weaknesses = []
        if metrics.quality_gate_pass_rate < 70:
            weaknesses.append("质量门控机制薄弱")
        if metrics.team_velocity_stability < 60:
            weaknesses.append("团队交付不稳定")
        if metrics.throughput_velocity < 15:
            weaknesses.append("开发效率低下")
        if metrics.defect_density > 15:
            weaknesses.append("代码质量待改善")
        if metrics.cycle_time_days > 30:
            weaknesses.append("交付周期过长")
        return weaknesses or ["整体表现均衡"]

    def _generate_recommendations(self, metrics: ProcessMetrics, maturity: ProcessMaturityLevel) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if maturity.value < 3:
            recommendations.extend([
                "建立标准化开发流程",
                "引入敏捷实践和工具",
                "实施代码审查和自动化测试"
            ])

        if metrics.cycle_time_days > 21:
            recommendations.append("优化需求管理和开发流程，减少周期时间")

        if metrics.defect_density > 10:
            recommendations.append("加强代码质量控制，引入静态分析工具")

        if metrics.quality_gate_pass_rate < 85:
            recommendations.append("完善质量门控，建立自动化检查机制")

        if metrics.team_velocity_stability < 70:
            recommendations.append("稳定团队组成，减少人员流动对交付的影响")

        return recommendations or ["继续保持当前良好实践"]

    def establish_baseline(self, historical_data: List[ProcessMetrics]) -> Dict[str, float]:
        """建立性能基线"""
        if not historical_data:
            return {}

        # 计算平均值和标准差
        cycle_times = [m.cycle_time_days for m in historical_data]
        defect_densities = [m.defect_density for m in historical_data]
        throughputs = [m.throughput_velocity for m in historical_data]
        quality_rates = [m.quality_gate_pass_rate for m in historical_data]
        stabilities = [m.team_velocity_stability for m in historical_data]

        def mean_std(data: List[float]) -> tuple[float, float]:
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            std = variance ** 0.5
            return mean, std

        baseline = {
            "cycle_time_mean": mean_std(cycle_times)[0],
            "cycle_time_std": mean_std(cycle_times)[1],
            "defect_density_mean": mean_std(defect_densities)[0],
            "defect_density_std": mean_std(defect_densities)[1],
            "throughput_mean": mean_std(throughputs)[0],
            "throughput_std": mean_std(throughputs)[1],
            "quality_rate_mean": mean_std(quality_rates)[0],
            "quality_rate_std": mean_std(quality_rates)[1],
            "stability_mean": mean_std(stabilities)[0],
            "stability_std": mean_std(stabilities)[1]
        }

        return baseline


def main():
    """主函数：演示流程评估"""
    # 示例数据
    sample_metrics = ProcessMetrics(
        cycle_time_days=12.5,
        defect_density=8.2,
        throughput_velocity=25.0,
        quality_gate_pass_rate=87.5,
        team_velocity_stability=78.3
    )

    # 创建评估引擎
    engine = ProcessAssessmentEngine()

    # 执行评估
    assessment = engine.assess_process(sample_metrics)

    # 输出结果
    print("=== 流程评估报告 ===")
    print(f"当前成熟度等级: {assessment.current_maturity.name} (Level {assessment.current_maturity.value})")
    print(".1f"
    print("\n优势:")
    for strength in assessment.strengths:
        print(f"  • {strength}")

    print("\n劣势:")
    for weakness in assessment.weaknesses:
        print(f"  • {weakness}")

    print("\n改进建议:")
    for rec in assessment.recommendations:
        print(f"  • {rec}")

    # 建立基线示例
    historical_data = [
        ProcessMetrics(15.0, 10.0, 20.0, 80.0, 70.0),
        ProcessMetrics(14.0, 9.0, 22.0, 85.0, 75.0),
        ProcessMetrics(13.0, 8.5, 24.0, 88.0, 77.0),
        ProcessMetrics(12.5, 8.2, 25.0, 87.5, 78.3)
    ]

    baseline = engine.establish_baseline(historical_data)
    print("
=== 性能基线 ===")
    for key, value in baseline.items():
        print(".2f")


if __name__ == "__main__":
    main()