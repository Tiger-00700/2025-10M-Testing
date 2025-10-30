# 数据驱动测试示例
import pytest
import yaml

def load_test_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@pytest.mark.parametrize("test_data", load_test_data('test_data.yaml'))
def test_data_processing(test_data):
    input_data = test_data['input']
    expected_output = test_data['expected']
    
    # 调用被测函数
    actual_output = process_data(input_data)
    
    # 验证结果
    assert actual_output == expected_output
