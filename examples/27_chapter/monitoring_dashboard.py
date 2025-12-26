#!/usr/bin/env python3
"""
工具链监控仪表板
使用Streamlit构建可视化监控界面
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time
from typing import Dict, Any, List

# 模拟监控数据
def get_mock_metrics() -> Dict[str, Any]:
    """获取模拟监控指标"""
    return {
        "timestamp": datetime.now(),
        "tools": {
            "great_expectations": {
                "status": "healthy",
                "validations_today": 145,
                "success_rate": 0.98,
                "avg_response_time": 2.3
            },
            "jmeter": {
                "status": "healthy",
                "active_tests": 3,
                "total_requests": 125000,
                "error_rate": 0.015
            },
            "selenium_grid": {
                "status": "warning",
                "active_sessions": 8,
                "available_nodes": 12,
                "queue_length": 2
            }
        },
        "system": {
            "cpu_usage": 65.5,
            "memory_usage": 78.2,
            "disk_usage": 45.8,
            "network_io": 125.3
        },
        "integrations": {
            "api_calls": 2340,
            "success_rate": 0.995,
            "avg_latency": 45.2
        }
    }

def create_status_cards(metrics: Dict[str, Any]):
    """创建状态卡片"""
    st.header("🛠️ 工具状态概览")

    col1, col2, col3 = st.columns(3)

    tools = metrics["tools"]

    with col1:
        status = tools["great_expectations"]["status"]
        color = "🟢" if status == "healthy" else "🟡" if status == "warning" else "🔴"
        st.metric(
            "Great Expectations",
            f"{color} {status.title()}",
            f"验证: {tools['great_expectations']['validations_today']}"
        )

    with col2:
        status = tools["jmeter"]["status"]
        color = "🟢" if status == "healthy" else "🟡" if status == "warning" else "🔴"
        st.metric(
            "JMeter",
            f"{color} {status.title()}",
            f"活跃测试: {tools['jmeter']['active_tests']}"
        )

    with col3:
        status = tools["selenium_grid"]["status"]
        color = "🟢" if status == "healthy" else "🟡" if status == "warning" else "🔴"
        st.metric(
            "Selenium Grid",
            f"{color} {status.title()}",
            f"活跃会话: {tools['selenium_grid']['active_sessions']}"
        )

def create_performance_charts(metrics: Dict[str, Any]):
    """创建性能图表"""
    st.header("📊 性能指标")

    # 系统资源使用情况
    system_data = metrics["system"]

    col1, col2 = st.columns(2)

    with col1:
        # CPU和内存使用率
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=system_data["cpu_usage"],
            title={"text": "CPU使用率 (%)"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "darkblue"}}
        ))
        st.plotly_chart(fig)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=system_data["memory_usage"],
            title={"text": "内存使用率 (%)"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "darkgreen"}}
        ))
        st.plotly_chart(fig)

    # 工具性能趋势 (模拟历史数据)
    st.subheader("工具性能趋势")

    # 生成模拟历史数据
    timestamps = [datetime.now() - timedelta(minutes=i) for i in range(60, 0, -5)]
    ge_response_times = [2.3 + (i % 10 - 5) * 0.1 for i in range(len(timestamps))]
    jmeter_errors = [0.015 + (i % 8 - 4) * 0.001 for i in range(len(timestamps))]

    df = pd.DataFrame({
        "时间": timestamps,
        "GE响应时间": ge_response_times,
        "JMeter错误率": jmeter_errors
    })

    fig = px.line(df, x="时间", y=["GE响应时间", "JMeter错误率"],
                  title="性能指标趋势")
    st.plotly_chart(fig)

def create_integration_monitoring(metrics: Dict[str, Any]):
    """创建集成监控"""
    st.header("🔗 集成监控")

    integrations = metrics["integrations"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("API调用", f"{integrations['api_calls']:,}")

    with col2:
        st.metric("成功率", f"{integrations['success_rate']:.1%}")

    with col3:
        st.metric("平均延迟", f"{integrations['avg_latency']}ms")

    # 集成状态表格
    st.subheader("集成链路状态")

    integration_status = [
        {"服务": "GE → 数据管道", "状态": "🟢 正常", "延迟": "45ms", "成功率": "99.5%"},
        {"服务": "JMeter → 测试框架", "状态": "🟢 正常", "延迟": "32ms", "成功率": "99.8%"},
        {"服务": "Selenium → UI测试", "状态": "🟡 警告", "延迟": "78ms", "成功率": "98.2%"},
        {"服务": "监控 → 告警系统", "状态": "🟢 正常", "延迟": "12ms", "成功率": "100%"},
    ]

    df = pd.DataFrame(integration_status)
    st.dataframe(df, use_container_width=True)

def create_alerts_section():
    """创建告警部分"""
    st.header("🚨 活动告警")

    alerts = [
        {
            "级别": "警告",
            "时间": "2024-01-15 14:30:25",
            "消息": "Selenium Grid节点队列长度超过阈值",
            "影响": "UI测试可能延迟"
        },
        {
            "级别": "信息",
            "时间": "2024-01-15 14:25:10",
            "消息": "Great Expectations完成每日验证任务",
            "影响": "数据质量检查正常"
        }
    ]

    for alert in alerts:
        if alert["级别"] == "警告":
            st.warning(f"**{alert['级别']}** - {alert['消息']}")
        elif alert["级别"] == "信息":
            st.info(f"**{alert['级别']}** - {alert['消息']}")
        else:
            st.error(f"**{alert['级别']}** - {alert['消息']}")

        st.caption(f"时间: {alert['时间']} | 影响: {alert['影响']}")
        st.divider()

def main():
    """主函数"""
    st.set_page_config(
        page_title="工具链监控仪表板",
        page_icon="📊",
        layout="wide"
    )

    st.title("🔧 大数据测试工具链监控仪表板")

    # 侧边栏
    st.sidebar.header("控制面板")
    auto_refresh = st.sidebar.checkbox("自动刷新", value=True)
    refresh_interval = st.sidebar.slider("刷新间隔(秒)", 5, 60, 30)

    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

    # 获取监控数据
    metrics = get_mock_metrics()

    # 显示最后更新时间
    st.sidebar.caption(f"最后更新: {metrics['timestamp'].strftime('%H:%M:%S')}")

    # 创建各个部分
    create_status_cards(metrics)
    create_performance_charts(metrics)
    create_integration_monitoring(metrics)
    create_alerts_section()

    # 页脚
    st.markdown("---")
    st.caption("© 2024 大数据测试工具链监控系统 | 版本 1.0.0")

if __name__ == "__main__":
    main()