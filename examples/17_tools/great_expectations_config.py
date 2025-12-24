# examples/17_tools/great_expectations_config.py
import great_expectations as ge
from great_expectations.core.expectation_configuration import ExpectationConfiguration

# 创建数据上下文
context = ge.get_context()

# 定义数据源
datasource_config = {
    "name": "bigdata_datasource",
    "class_name": "Datasource",
    "module_name": "great_expectations.datasource",
    "execution_engine": {
        "class_name": "SparkDFExecutionEngine"
    },
    "data_connectors": {
        "default_inferred_data_connector_name": {
            "class_name": "InferredAssetFilesystemDataConnector",
            "base_directory": "/data/input",
            "default_regex": {
                "pattern": "(.*)\\.csv",
                "group_names": ["data_asset_name"]
            }
        }
    }
}

# 添加数据源
context.add_datasource(**datasource_config)

# 创建期望套件
suite = context.create_expectation_suite("customer_data_suite", overwrite_existing=True)

# 添加数据质量期望
expectation_configurations = [
    ExpectationConfiguration(
        expectation_type="expect_table_row_count_to_be_between",
        kwargs={"min_value": 1000, "max_value": 1000000}
    ),
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "customer_id"}
    ),
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_unique",
        kwargs={"column": "customer_id"}
    ),
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_be_in_set",
        kwargs={"column": "status", "value_set": ["active", "inactive", "pending"]}
    ),
    ExpectationConfiguration(
        expectation_type="expect_column_values_to_match_regex",
        kwargs={"column": "email", "regex": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"}
    )
]

# 将期望添加到套件
for config in expectation_configurations:
    suite.add_expectation(config)

# 保存期望套件
context.save_expectation_suite(suite)

print("Great Expectations configuration completed successfully!")