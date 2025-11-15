# ETL流程自动化测试示例
@pytest.mark.parametrize("data_sample,expected_transformation", get_test_cases())
def test_etl_transformation(data_sample, expected_transformation):
    # 执行ETL流程
    result = run_etl_pipeline(data_sample)

    # 验证结果
    assert verify_transformation_rules(result, expected_transformation)
    assert validate_business_rules(result)
    assert check_data_quality(result)
