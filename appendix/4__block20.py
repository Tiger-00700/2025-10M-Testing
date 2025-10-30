def expect_column_values_to_follow_business_rule(validator, column_name, business_rule_func, column_list=None):
    """
    自定义期望：验证列值遵循特定业务规则
    
    Args:
        validator: Great Expectations验证器实例
        column_name: 要验证的列名
        business_rule_func: 业务规则函数，接受值并返回布尔值
        column_list: 要使用的其他列（如果业务规则需要）
    
    Returns:
        验证结果
    """
    if column_list is None:
        column_list = []
    
    # 获取数据
    df = validator.active_batch.data.dataframe
    
    # 定义验证函数
    def validate(row):
        if column_list:
            values = [row[col] for col in column_list]
            return business_rule_func(row[column_name], *values)
        else:
            return business_rule_func(row[column_name])
    
    # 应用验证
    df["_valid"] = df.apply(validate, axis=1)
    success_count = df["_valid"].sum()
    total_count = len(df)
    
    # 创建结果
    result = {
        "success": success_count == total_count,
        "result": {
            "element_count": total_count,
            "unexpected_count": total_count - success_count,
            "unexpected_percent": (total_count - success_count) / total_count * 100 if total_count > 0 else 0
        }
    }
    
    return result

# 使用示例
def validate_account_balance(balance, min_balance=-1000, max_balance=1000000):
    return min_balance <= balance <= max_balance

result = expect_column_values_to_follow_business_rule(
    validator, 
    "account_balance", 
    validate_account_balance
)
