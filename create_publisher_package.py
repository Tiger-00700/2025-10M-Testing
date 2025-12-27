import zipfile
import os
import shutil
from pathlib import Path

def create_publisher_package():
    """创建出版社交付包"""

    # 主文件
    main_docx = "1225全书定稿_perfectly_fixed.docx"

    # 引用的文件列表（从之前的分析中提取）
    referenced_files = [
        "/tools/qa_summary.py",
        "examples/01_intro/data_factory.py",
        "examples/01_intro/data_factory.py。",
        "examples/01_intro/masking_policy_demo.py",
        "examples/01_intro/masking_policy_demo.py。",
        "examples/01_intro/qa_summary.py",
        "examples/01_intro/simple_data_pipeline.md",
        "examples/01_intro/simple_data_pipeline.md。",
        "examples/01_intro/tools/qa_summary.py",
        "examples/02_quality_metrics/contract_example.yml；本地可用",
        "examples/02_quality_metrics/quality_rules.yml",
        "examples/02_quality_metrics/rule_runner.py",
        "examples/04_env/env_health_check.py",
        "examples/06_ingest/ai_anomaly_deployment.py",
        "examples/06_ingest/ai_ml_test_methods.yml",
        "examples/06_ingest/batch_reconciliation.py",
        "examples/06_ingest/batch_reconciliation.py。",
        "examples/06_ingest/ecommerce_order_test.py",
        "examples/06_ingest/iot_ai_ingestion_test.py",
        "examples/06_ingest/multi_cloud_ai_deployment.py",
        "examples/06_ingest/report_reconciliation.py",
        "examples/06_ingest/tool_eval_checklist.yml。",
        "examples/07_storage/ai_driven_testing_framework.yml",
        "examples/07_storage/cloud_provider_specific_configs.yml",
        "examples/07_storage/cloud_storage_focus_points.yml",
        "examples/07_storage/consistency_reliability_focus_points.yml",
        "examples/07_storage/container_storage_testing_guide.yml",
        "examples/07_storage/dw_lakehouse_focus_points.yml",
        "examples/07_storage/emerging_storage_technologies.yml",
        "examples/07_storage/future_outlook.yml",
        "examples/07_storage/hdfs_focus_points.yml",
        "examples/07_storage/nosql_focus_points.yml",
        "examples/07_storage/production_case_studies.yml",
        "examples/07_storage/rdbms_focus_points.yml",
        "examples/07_storage/storage_fault_injection_chaos.yml",
        "examples/07_storage/storage_testing_automation_framework.yml",
        "examples/07_storage/storage_testing_best_practices.yml",
        "examples/07_storage/storage_testing_tools_guide.yml",
        "examples/07_storage/testing_standardization_framework.yml",
        "examples/08_processing/ai_driven_processing_test.yml",
        "examples/08_processing/automation_tools_practices.yml",
        "examples/08_processing/batch_test_methods.yml",
        "examples/08_processing/emerging_technologies_test.yml",
        "examples/08_processing/future_processing_outlook.yml",
        "examples/08_processing/ml_pipeline_test.yml",
        "examples/08_processing/performance_scalability_test.yml",
        "examples/08_processing/stream_test_techniques.yml",
        "examples/09_quality/issue_identification_fix.yml",
        "examples/09_quality/monitoring_alert_strategies.yml",
        "examples/09_quality/quality_dimensions.yml",
        "examples/09_quality/quality_testing_methods.yml",
        "examples/09_quality/tools_practice_cases.yml",
        "examples/10_security/access_control_tests.yml",
        "examples/10_security/audit_artifacts_checklist.md",
        "examples/10_security/compliance_focus_points.yml",
        "examples/10_security/data_masking_tests.yml",
        "examples/10_security/devsecops_integration.yml",
        "examples/10_security/platform_automation_trends.yml",
        "examples/10_security/quantum_security_threats.yml",
        "examples/10_security/security_test_methods.yml",
        "examples/11_analytics/ai_ml_test_methods.yml",
        "examples/11_analytics/analytics_tools_cases.yml",
        "examples/11_analytics/audit_artifacts_checklist.md",
        "examples/11_analytics/bi_report_test_methods.yml",
        "examples/11_analytics/data_mining_test_methods.yml",
        "examples/11_analytics/visualization_test_methods.yml",
        "examples/12_governance/automation_tools.yml",
        "examples/12_governance/disaster_recovery.yml",
        "examples/12_governance/disaster_recovery.yml））：",
        "examples/12_governance/env_architecture_design.yml",
        "examples/12_governance/env_maturity_assessment.md",
        "examples/12_governance/env_maturity_assessment.md））：",
        "examples/12_governance/env_multi_cluster_config.yml））：",
        "examples/12_governance/env_switching_tools.py",
        "examples/12_governance/env_switching_tools.py））：",
        "examples/12_governance/env_types_comparison.yml",
        "examples/12_governance/monitoring_config.yml））：",
        "examples/12_governance/multi_cluster_architecture.yml",
        "examples/12_governance/quota_policy.yml",
        "examples/12_governance/quota_policy.yml））：",
        "examples/12_governance/tools_comparison.yml",
        "examples/13_data_gov/ai_governance_config.yml",
        "examples/13_data_gov/ai_governance_monitor.py",
        "examples/13_data_gov/contract_example.yml > 引用附件: examples/09_quality/rule",
        "examples/13_data_gov/contract_example.yml",
        "examples/13_data_gov/governance_recommendations.yml",
        "examples/13_data_gov/lifecycle_management.py",
        "examples/13_data_gov/lifecycle_measures.yml",
        "examples/13_data_gov/lifecycle_recommendations.yml",
        "examples/13_data_gov/lifecycle_stages.yml",
        "examples/13_data_gov/masking_policy_demo.py",
        "examples/13_data_gov/replay_pipeline.py",
        "examples/13_data_gov/risk_assessment.yml",
        "examples/14_monitoring/alerting_rules.yml",
        "examples/14_monitoring/alerting_strategy.md",
        "examples/14_monitoring/dashboard_template.json",
        "examples/14_monitoring/monitoring_config.yml",
        "examples/14_monitoring/monitoring_pipeline.py",
        "examples/15_framework/alert_rules.yml 完成情况: 已标准化",
        "examples/15_framework/alerting_system.md 完成情况: 已完成",
        "examples/15_framework/alertmanager_config.yml",
        "examples/15_framework/distributed_tracing.md 完成情况: 已标准化",
        "examples/15_framework/distributed_tracing.py",
        "examples/15_framework/governance_enforcement.py",
        "examples/15_framework/governance_policy.yml",
        "examples/15_framework/log_analyzer.py",
        "examples/15_framework/logging_pipeline.md 完成情况: 已完成",
        "examples/15_framework/logs_aggregation.md 完成情况: 已标准化",
        "examples/15_framework/logstash_pipeline.conf",
        "examples/15_framework/metrics_manager.py",
        "examples/15_framework/metrics_pipeline.md",
        "examples/15_framework/metrics_pipeline.md 完成情况: 已标准化",
        "examples/15_framework/monitoring_architecture.md",
        "examples/15_framework/monitoring_stack.yml",
        "examples/15_framework/observability_basics.md",
        "examples/15_framework/observability_governance.md 完成情况: 已完成",
        "examples/15_framework/observability_governance.md 完成情况: 已标准化",
        "examples/15_framework/observability_implementation.yml",
        "examples/15_framework/observability_platform.md 完成情况: 已完成",
        "examples/15_framework/observability_platform.md 完成情况: 已标准化",
        "examples/15_framework/observability_test_framework.py",
        "examples/15_framework/observability_testing.md 完成情况: 已完成",
        "examples/15_framework/otel_collector_config.yml",
        "examples/15_framework/platform_deployment.yml",
        "examples/15_framework/platform_monitoring.py",
        "examples/15_framework/prometheus_metrics.yml",
        "examples/15_framework/smart_alerting.py",
        "examples/15_framework/testing_strategy.md 完成情况: 已标准化",
        "examples/15_framework/tracing_pipeline.md 完成情况: 已完成",
        "examples/16_tools/cloud_integration_framework.py",
        "examples/16_tools/cloud_integration_framework.py 完成情况: 已完成",
        "examples/16_tools/cloud_integration_framework.py):",
        "examples/16_tools/cloud_monitoring_collector.py",
        "examples/16_tools/cloud_monitoring_collector.py 完成情况: 已完成",
        "examples/16_tools/cloud_monitoring_collector.py):",
        "examples/16_tools/cloud_native_testing_toolchain.py",
        "examples/16_tools/cloud_native_testing_toolchain.py 完成情况: 已完成",
        "examples/16_tools/cloud_native_testing_toolchain.py):",
        "examples/16_tools/data_consistency_validator.py",
        "examples/16_tools/data_consistency_validator.py 完成情况: 已完成",
        "examples/16_tools/data_consistency_validator.py):",
        "examples/16_tools/deployment_config.yml",
        "examples/16_tools/deployment_orchestrator.py",
        "examples/16_tools/deployment_orchestrator.py 完成情况: 已完成",
        "examples/16_tools/deployment_orchestrator.py):",
        "examples/16_tools/extension_config.yml",
        "examples/16_tools/framework_evaluation.yml",
        "examples/16_tools/hybrid_cloud_test_coordinator.py",
        "examples/16_tools/hybrid_cloud_test_coordinator.py 完成情况: 已完成",
        "examples/16_tools/hybrid_cloud_test_coordinator.py):",
        "examples/16_tools/multi_cloud_security_framework.py",
        "examples/16_tools/multi_cloud_security_framework.py 完成情况: 已完成",
        "examples/16_tools/multi_cloud_security_framework.py):",
        "examples/16_tools/multi_cloud_test_checklist.yml",
        "examples/16_tools/multi_cloud_test_checklist.yml 完成情况: 已完成",
        "examples/16_tools/multi_cloud_test_checklist.yml):",
        "examples/16_tools/test_case_management.yml",
        "examples/16_tools/test_workflow.yml",
        "examples/16_tools/tool_eval_checklist.yml",
        "examples/17_observability/scenario_decomposition.yml",
        "examples/17_tools/automation_framework.md 完成情况: 已完成",
        "examples/17_tools/case_retrospective.md 完成情况: 已完成",
        "examples/17_tools/case_retrospective.yml",
        "examples/17_tools/experience_repository.py",
        "examples/17_tools/quality_metrics.yml",
        "examples/17_tools/result_validation.md 完成情况: 已完成",
        "examples/17_tools/result_validator.py",
        "examples/17_tools/scenario_analysis.md 完成情况: 已完成",
        "examples/17_tools/test_automation_framework.py",
        "examples/17_tools/test_case_design.md 完成情况: 已完成",
        "examples/17_tools/test_case_template.yml",
        "examples/18_cases/ 完成情况: 已完成",
        "examples/18_cases/autonomous_test_cases.yml",
        "examples/18_cases/autonomous_test_validator.py 完成情况: 已完成",
        "examples/18_cases/ecommerce_funnel_check.py 完成情况: 已完成",
        "examples/18_cases/financial_test_cases.yml",
        "examples/18_cases/financial_test_validator.py",
        "examples/18_cases/fraud_feature_check_stub.py 完成情况: 已完成",
        "examples/18_cases/government_test_cases.yml",
        "examples/18_cases/government_test_validator.py",
        "examples/18_cases/healthcare_data_validation_stub.py 完成情况: 已完成",
        "examples/18_cases/healthcare_test_cases.yml",
        "examples/18_cases/industry_experience_repository.py",
        "examples/18_cases/industry_maturity_model.yml",
        "examples/18_cases/industry_retrospective.yml",
        "examples/18_cases/internet_test_cases.yml",
        "examples/18_cases/internet_test_validator.py",
        "examples/18_cases/iot_alert_replay_stub.py 完成情况: 已完成",
        "examples/18_cases/iot_test_cases.yml",
        "examples/18_cases/iot_test_validator.py",
        "examples/18_cases/maturity_assessment.py",
        "examples/18_cases/smartcity_test_cases.yml",
        "examples/18_cases/smartcity_test_validator.py 完成情况: 已完成",
        "examples/19_industry/data_ingestion_pipeline.py",
        "examples/20_evolution/alibaba_ack_deployment.yml",
        "examples/20_evolution/architecture_design.py",
        "examples/20_evolution/architecture_design.py 完成情况: 已完成",
        "examples/20_evolution/architecture_design.yml",
        "examples/20_evolution/autonomous_variant.yml",
        "examples/20_evolution/aws_eks_deployment.yml",
        "examples/20_evolution/case_requirements.py",
        "examples/20_evolution/case_requirements.yml",
        "examples/20_evolution/cost_benefit_analysis.yml",
        "examples/20_evolution/docker_compose.yml",
        "examples/20_evolution/ecommerce_variant.yml",
        "examples/20_evolution/finance_variant.yml",
        "examples/20_evolution/healthcare_variant.yml",
        "examples/20_evolution/implementation_steps.py",
        "examples/20_evolution/implementation_steps.py 完成情况: 已完成",
        "examples/20_evolution/implementation_steps.yml",
        "examples/20_evolution/iot_variant.yml",
        "examples/20_evolution/kubernetes_deployment.yml",
        "examples/20_evolution/lessons_learned.py",
        "examples/20_evolution/lessons_learned.py 完成情况: 已完成",
        "examples/20_evolution/lessons_learned.yml",
        "examples/20_evolution/ml_anomaly_detection.yml",
        "examples/20_evolution/ml_automated_decisions.yml",
        "examples/20_evolution/ml_batch_training.yml",
        "examples/20_evolution/ml_realtime_features.yml",
        "examples/20_evolution/roi_calculator.py",
        "examples/20_evolution/smartcity_variant.yml",
        "examples/20_evolution/social_variant.yml",
        "examples/20_evolution/testing_validation.py",
        "examples/20_evolution/testing_validation.py 完成情况: 已完成",
        "examples/20_evolution/testing_validation.yml",
        "examples/21_project/agile_testing_workflow.py 完成情况: 已完成",
        "examples/21_project/devops_testing.yml",
        "examples/21_project/project_management.yml",
        "examples/21_project/project_management_framework.py 完成情况: 已完成",
        "examples/21_project/quality_metrics_dashboard.py 完成情况: 已完成",
        "examples/21_project/risk_management_system.py 完成情况: 已完成",
        "examples/21_project/team_collaboration_model.py 完成情况: 已完成",
        "examples/22_cicd/automation_deployment/automation_deployment.py 完成情况: 已完",
        "examples/22_cicd/bottleneck_analysis/bottleneck_analysis.py 完成情况: 已完成",
        "examples/22_cicd/process_assessment/process_assessment.py 完成情况: 已完成",
        "examples/22_cicd/process_monitoring/process_monitoring.py 完成情况: 已完成",
        "examples/22_cicd/process_resilience/process_resilience.py 完成情况: 已完成",
        "examples/23_chapter/",
        "examples/23_chapter/agile_quality_improvement.yml",
        "examples/23_chapter/ai_implementation_strategy.yml",
        "examples/23_chapter/alm_platforms.yml",
        "examples/23_chapter/benchmarking_management.yml",
        "examples/23_chapter/blockchain_quality_traceability.yml",
        "examples/23_chapter/change_management_framework.yml",
        "examples/23_chapter/cicd_testing_strategy.yml",
        "examples/23_chapter/cost_benefit_analysis.yml",
        "examples/23_chapter/defect_prediction_features.yml",
        "examples/23_chapter/deployment_strategy.yml",
        "examples/23_chapter/devops_toolchain_integration.yml",
        "examples/23_chapter/digital_twin_quality_assessment.yml",
        "examples/23_chapter/dmaic_improvement_method.yml",
        "examples/23_chapter/dynamic_testing_tools.yml",
        "examples/23_chapter/edge_quality_monitoring.yml",
        "examples/23_chapter/gitops_testing_integration.yml",
        "examples/23_chapter/improvement_roadmap.yml",
        "examples/23_chapter/integration_patterns.yml",
        "examples/23_chapter/kpi_design_framework.yml",
        "examples/23_chapter/maturity_assessment_methods.yml",
        "examples/23_chapter/metaverse_quality_assessment.yml",
        "examples/23_chapter/model_evaluation_metrics.yml",
        "examples/23_chapter/monitoring_metrics_system.yml",
        "examples/23_chapter/monitoring_system_integration.yml",
        "examples/23_chapter/pdca_improvement_cycle.yml",
        "examples/23_chapter/performance_monitoring_tools.yml",
        "examples/23_chapter/quality_benefit_quantification.yml",
        "examples/23_chapter/quality_cost_breakdown.yml",
        "examples/23_chapter/quality_culture_building.yml",
        "examples/23_chapter/quality_dashboard.yml",
        "examples/23_chapter/quality_maturity_model.yml",
        "examples/23_chapter/quality_portal_platforms.yml",
        "examples/23_chapter/quality_trend_prediction.yml",
        "examples/23_chapter/quantum_quality_optimization.yml",
        "examples/23_chapter/reporting_platform_integration.yml",
        "examples/23_chapter/roi_calculation_model.yml",
        "examples/23_chapter/root_cause_analysis.py",
        "examples/23_chapter/security_testing_tools.yml",
        "examples/23_chapter/skill_development_training.yml",
        "examples/23_chapter/static_analysis_tools.yml",
        "examples/23_chapter/technology_convergence_strategy.yml",
        "examples/23_chapter/test_case_generation.yml",
        "examples/23_chapter/test_case_prioritization.py",
        "examples/23_chapter/test_management_platforms.yml",
        "examples/23_chapter/tool_selection_framework.yml",
        "examples/23_chapter/toolchain_best_practices.yml",
        "examples/24_chapter/",
        "examples/24_chapter/ai_migration_execution.yml",
        "examples/24_chapter/ai_migration_planning.yml",
        "examples/24_chapter/ai_monitoring_optimization.yml",
        "examples/24_chapter/application_migration_tools.yml",
        "examples/24_chapter/business_effectiveness_evaluation.yml",
        "examples/24_chapter/business_risks.yml",
        "examples/24_chapter/cicd_migration_integration.yml",
        "examples/24_chapter/cloud_native_migration_platforms.yml",
        "examples/24_chapter/common_drill_issues.yml",
        "examples/24_chapter/contingency_planning.yml",
        "examples/24_chapter/continuous_improvement.yml",
        "examples/24_chapter/continuous_improvement_framework.yml",
        "examples/24_chapter/cross_cloud_data_consistency.yml",
        "examples/24_chapter/data_synchronization_architecture.yml",
        "examples/24_chapter/dr_drill_best_practices.yml",
        "examples/24_chapter/dr_drill_process.yml",
        "examples/24_chapter/dr_drill_types.yml",
        "examples/24_chapter/dr_tiers.yml",
        "examples/24_chapter/drill_environment_setup.yml",
        "examples/24_chapter/drill_execution_flow.yml",
        "examples/24_chapter/drill_monitoring_metrics.yml",
        "examples/24_chapter/drill_monitoring_metrics.yml",
        "examples/24_chapter/failover_strategies.yml",
        "examples/24_chapter/feedback_loop_mechanism.yml",
        "examples/24_chapter/ha_design_principles.yml",
        "examples/24_chapter/hybrid_cloud_patterns.yml",
        "examples/24_chapter/iac_migration_automation.yml",
        "examples/24_chapter/infrastructure_migration_tools.yml",
        "examples/24_chapter/knowledge_transfer_training.yml",
        "examples/24_chapter/migration_6r_strategy.yml",
        "examples/24_chapter/migration_assessment.yml",
        "examples/24_chapter/migration_automation.sh",
        "examples/24_chapter/migration_automation_script.py",
        "examples/24_chapter/migration_best_practices.yml",
        "examples/24_chapter/migration_decision_support.yml",
        "examples/24_chapter/migration_drill_scope.yml",
        "examples/24_chapter/migration_execution_plan.yml",
        "examples/24_chapter/migration_monitoring_metrics.yml",
        "examples/24_chapter/migration_pathways.yml",
        "examples/24_chapter/migration_risk_assessment.yml",
        "examples/24_chapter/migration_terraform.tf",
        "examples/24_chapter/migration_tool_evaluation_criteria.yml",
        "examples/24_chapter/monitoring_tools_integration.yml",
        "examples/24_chapter/multi_cloud_best_practices.yml",
        "examples/24_chapter/multi_cloud_native.yml",
        "examples/24_chapter/multi_cloud_security_governance.yml",
        "examples/24_chapter/multi_region_dr.yml",
        "examples/24_chapter/post_migration_operations.yml",
        "examples/24_chapter/quantitative_risk_assessment.yml",
        "examples/24_chapter/risk_matrix_analysis.yml",
        "examples/24_chapter/risk_mitigation_strategies.yml",
        "examples/24_chapter/risk_monitoring_framework.yml",
        "examples/24_chapter/risk_reporting_system.yml",
        "examples/24_chapter/security_incident_response.yml",
        "examples/24_chapter/technical_effectiveness_evaluation.yml",
        "examples/24_chapter/third_party_migration_platforms.yml",
        "examples/24_chapter/tool_selection_process.yml",
        "examples/25_chapter/cicd_pipeline.yml",
        "examples/25_chapter/devops_practices.md 完成情况: 已完成",
        "examples/25_chapter/environment_management.md 完成情况: 已完成",
        "examples/25_chapter/jenkins_pipeline.groovy",
        "examples/25_chapter/metrics_dashboard.py",
        "examples/25_chapter/observability_basics.md 完成情况: 已完成",
        "examples/25_chapter/pipeline_design.md 完成情况: 已完成",
        "examples/25_chapter/quality_gates.md 完成情况: 已完成",
        "examples/25_chapter/quality_gates.yml",
        "examples/25_chapter/team_collaboration.yml",
        "examples/25_chapter/terraform_environment.tf",
        "examples/25_chapter/test_data_manager.py",
        "examples/26_chapter/ad_attribution_check.py 完成情况: 已完成",
        "examples/26_chapter/ecommerce_funnel_check.py 完成情况: 已完成",
        "examples/26_chapter/failure_pattern_analysis.py 完成情况: 已完成",
        "examples/26_chapter/framework_template.yml",
        "examples/26_chapter/framework_template.yml 完成情况: 已完成",
        "examples/26_chapter/fraud_feature_check_stub.py 完成情况: 已完成",
        "examples/26_chapter/iot_alert_replay_stub.py 完成情况: 已完成",
        "examples/27_chapter/adapter_pattern.py",
        "examples/27_chapter/automated_operations.py",
        "examples/27_chapter/governance_dashboard.py",
        "examples/27_chapter/governance_framework.md 完成情况: 已完成",
        "examples/27_chapter/governance_policy.yml",
        "examples/27_chapter/integration_patterns.md 完成情况: 已完成",
        "examples/27_chapter/operations_management.md 完成情况: 已完成",
        "examples/27_chapter/toolchain_integration.yml",
        "examples/28_chapter/data_analysis.md 完成情况: 已完成",
        "examples/28_chapter/data_analysis_platform.py",
        "examples/28_chapter/monitoring_metrics.py",
        "examples/28_chapter/monitoring_system.md 完成情况: 已完成",
        "examples/28_chapter/observability_architecture.md 完成情况: 已完成",
        "examples/28_chapter/observability_config.yml",
        "examples/28_chapter/observability_trends.md 完成情况: 已完成",
        "examples/28_chapter/smart_alerting.md 完成情况: 已完成",
        "examples/28_chapter/smart_alerting.py",
        "examples/29_chapter/testing_toolchain_architecture.py",
        "examples/29_chapter/testing_tools_framework.md 完成情况: 已完成",
        "examples/29_chapter/tool_evaluation_framework.py",
        "examples/29_chapter/tool_selection_framework.md 完成情况: 已完成",
        "examples/29_chapter/toolchain_integration.md 完成情况: 已完成",
        "examples/29_chapter/toolchain_integration_config.py",
        "examples/30_chapter/ai_monitoring_automation.md 完成情况: 已完成",
        "examples/30_chapter/ai_monitoring_framework.py",
        "examples/30_chapter/monitoring_testing_practices.md 完成情况: 已完成",
        "examples/30_chapter/monitoring_toolchain.py",
        "examples/30_chapter/observability_architecture.md 完成情况: 已完成",
        "examples/30_chapter/observability_testing_framework.py",
        "examples/31_chapter/env_health_check.py 完成情况: 已完成",
        "examples/31_chapter/evaluation_scorecard.md",
        "examples/31_chapter/evaluation_scorecard.md 完成情况: 已完成",
        "examples/31_chapter/ingest/stream_test.py 完成情况: 已完成",
        "examples/31_chapter/migration_checklist.md 完成情况: 已完成",
        "examples/31_chapter/quality_rules.yml 完成情况: 已完成",
        "examples/33_chapter/ai_maturity_model.py",
        "examples/33_chapter/ai_test_case_generation.py",
        "examples/33_chapter/ai_testing_best_practices.md 完成情况: 已完成",
        "examples/33_chapter/ai_testing_evaluation.py",
        "examples/33_chapter/ai_testing_future.md 完成情况: 已完成",
        "examples/33_chapter/ai_testing_scenarios.md 完成情况: 已完成",
        "examples/34_chapter/ecosystem_construction.md 完成情况: 已完成",
        "examples/34_chapter/ecosystem_operations.py",
        "examples/34_chapter/platform_architecture.md 完成情况: 已完成",
        "examples/34_chapter/platform_core_capabilities.py",
        "examples/34_chapter/platform_governance.py",
        "examples/34_chapter/platform_implementation.md 完成情况: 已完成",
        "tools/pipeline/build_all.ps1 完成情况: 已完成",
        "tools/pipeline/data_lineage_check.py 完成情况: 已完成",
        "tools/reports/",
        "tools/reports/stream_batch_diff.md 完成情况: 已完成",
        "tools/reports/templates/",
        "tools/reports/templates/drift_approval_form.md",
        "tools/reports/templates/test_governance_framework.yml",
        "tools/reports/。",
        "tools/reports/）与审计所需字段。",
        "tools/validate_contracts.py",
        "tools/validate_quality_rules.py",
        "tools/validate_templates.py"
    ]

    # 清理和规范化文件路径
    cleaned_files = []
    for ref in referenced_files:
        # 移除路径开头的斜杠
        ref = ref.lstrip('/')
        # 移除一些特殊字符和后缀
        ref = ref.split(' 完成情况:')[0].strip()
        ref = ref.split('；')[0].strip()
        ref = ref.split('））：')[0].strip()
        ref = ref.split('））：')[0].strip()
        ref = ref.split('）：')[0].strip()
        ref = ref.split('）。')[0].strip()
        ref = ref.split('。')[0].strip()
        ref = ref.split(' > ')[0].strip()
        ref = ref.rstrip('.,;()[]')

        if ref and not ref.endswith('/') and ref != 'tools/reports/）与审计所需字段。':
            cleaned_files.append(ref)

    # 去重
    unique_files = list(set(cleaned_files))

    print(f"发现 {len(unique_files)} 个唯一引用文件")

    # 检查文件存在性并创建包
    existing_files = []
    missing_files = []

    for file_path in unique_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)

    print(f"存在的文件: {len(existing_files)}")
    print(f"缺失的文件: {len(missing_files)}")

    if missing_files:
        print("\n缺失的文件:")
        for mf in missing_files[:10]:  # 只显示前10个
            print(f"  {mf}")
        if len(missing_files) > 10:
            print(f"  ... 还有 {len(missing_files) - 10} 个")

    # 创建ZIP包
    zip_filename = "1225全书定稿_出版社交付包.zip"

    print(f"\n创建交付包: {zip_filename}")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加主文档
        if os.path.exists(main_docx):
            zipf.write(main_docx, f"书稿/{main_docx}")
            print(f"✓ 添加主文档: {main_docx}")
        else:
            print(f"❌ 主文档不存在: {main_docx}")

        # 添加引用文件
        for file_path in existing_files:
            try:
                # 保持目录结构
                arcname = f"引用附件/{file_path}"
                zipf.write(file_path, arcname)
            except Exception as e:
                print(f"❌ 添加文件失败 {file_path}: {e}")

        # 添加README说明文件
        readme_content = f"""# 2025大数据测试全书 - 出版社交付包

## 包内容说明

### 主书稿
- 1225全书定稿_perfectly_fixed.docx - 完整的标准化书稿

### 引用附件
包含书稿中引用的所有代码示例、配置文件和文档，共 {len(existing_files)} 个文件。

## 文件统计
- 主文档: 1个
- 引用文件: {len(existing_files)}个
- 缺失文件: {len(missing_files)}个

## 交付时间
{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 联系方式
如有问题请及时联系作者。
"""
        zipf.writestr("README.md", readme_content)

    # 获取包信息
    package_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB

    print(f"\n✅ 交付包创建完成!")
    print(f"📦 文件名: {zip_filename}")
    print(f"📏 大小: {package_size:.2f} MB")
    print(f"📄 包含文件数: {len(existing_files) + 1} (主文档 + 引用文件 + README)")

    if missing_files:
        print(f"\n⚠️  注意: {len(missing_files)} 个引用文件不存在，可能需要手动补充")

    return zip_filename, existing_files, missing_files

if __name__ == "__main__":
    create_publisher_package()