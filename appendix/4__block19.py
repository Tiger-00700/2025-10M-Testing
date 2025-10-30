import great_expectations as ge
from great_expectations.data_context import DataContext

# 初始化数据上下文
data_context = DataContext.create(project_root_dir="./great_expectations")

# 创建一个数据源配置
datasource_config = {
    "name": "spark_datasource",
    "class_name": "Datasource",
    "execution_engine": {
        "class_name": "SparkDFExecutionEngine"
    },
    "data_connectors": {
        "default_inferred_data_connector_name": {
            "class_name": "InferredAssetFilesystemDataConnector",
            "base_directory": "/data/input",
            "default_regex": {
                "group_names": ["data_asset_name"],
                "pattern": "(.*)\.csv"
            }
        }
    }
}

# 添加数据源
data_context.add_datasource(**datasource_config)

# 创建期望套件
expectation_suite_name = "data_quality_suite"
data_context.create_expectation_suite(expectation_suite_name, overwrite_existing=True)

# 定义批处理请求
batch_request = {
    "datasource_name": "spark_datasource",
    "data_connector_name": "default_inferred_data_connector_name",
    "data_asset_name": "test_data"
}

# 运行验证
validator = data_context.get_validator(
    batch_request=batch_request,
    expectation_suite_name=expectation_suite_name
)

# 添加期望值
validator.expect_column_values_to_not_be_null("customer_id")
validator.expect_column_values_to_be_between("age", 18, 100)
validator.expect_column_values_to_match_regex("email", r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
validator.expect_column_distinct_values_to_be_in_set("status", ["active", "inactive", "pending"])
validator.expect_column_values_to_be_unique("transaction_id")

# 保存期望套件
validator.save_expectation_suite(discard_failed_expectations=False)

# 运行验证
validation_result = data_context.run_validation_operator(
    "action_list_operator",
    assets_to_validate=[{
        "batch_request": batch_request,
        "expectation_suite_name": expectation_suite_name
    }]
)

# 生成数据文档
data_context.build_data_docs()
