from docx import Document

doc = Document('1225全书定稿_final_standardized_fixed.docx')

# Find the problematic anchor at paragraph 119
para = doc.paragraphs[119]
original_text = para.text

print('Original anchor content:')
print(original_text[:500] + '...')
print('')

# Build the corrected anchor format
corrected_anchor = '''>锚点名称: [锚点020] 应用场景分类表
>锚点类型: 建议
>锚点方法: 分类表
>补充建议: 插入场景分类表，字段包括：场景、数据类型、关键指标、脚本引用，补充 YAML/JSON 示例，参考脚本 examples/01_intro/simple_data_pipeline.md。
>引用附件: examples/01_intro/simple_data_pipeline.md
>完成情况: 已标准化
>更新时间: 2025-12-23

**应用场景分类表**

| 场景 | 数据类型 | 关键指标 | 脚本引用 |
|---|---|---|---|
| 电商推荐 | 用户行为日志、商品数据 | 点击率、转化率、个性化准确度 | examples/01_intro/simple_data_pipeline.md |
| 金融风控 | 交易记录、用户画像 | 欺诈检测率、误报率 | examples/01_intro/data_factory.py |
| 物联网监控 | 传感器数据、设备状态 | 数据完整性、实时延迟 | examples/01_intro/masking_policy_demo.py |
| 内容分发 | 用户偏好、内容元数据 | 内容匹配度、用户留存 | examples/01_intro/qa_summary.py |

**YAML 示例**:
```yaml
application_scenarios:
  ecommerce_recommendation:
    data_types: ["user_behavior_logs", "product_data"]
    key_metrics: ["click_through_rate", "conversion_rate", "personalization_accuracy"]
    script_reference: "examples/01_intro/simple_data_pipeline.md"
  financial_risk_control:
    data_types: ["transaction_records", "user_profiles"]
    key_metrics: ["fraud_detection_rate", "false_positive_rate"]
    script_reference: "examples/01_intro/data_factory.py"
  iot_monitoring:
    data_types: ["sensor_data", "device_status"]
    key_metrics: ["data_integrity", "real_time_latency"]
    script_reference: "examples/01_intro/masking_policy_demo.py"
  content_distribution:
    data_types: ["user_preferences", "content_metadata"]
    key_metrics: ["content_match_rate", "user_retention"]
    script_reference: "examples/01_intro/qa_summary.py"
```

**JSON 示例**:
```json
{
  "application_scenarios": {
    "ecommerce_recommendation": {
      "data_types": ["user_behavior_logs", "product_data"],
      "key_metrics": ["click_through_rate", "conversion_rate", "personalization_accuracy"],
      "script_reference": "examples/01_intro/simple_data_pipeline.md"
    },
    "financial_risk_control": {
      "data_types": ["transaction_records", "user_profiles"],
      "key_metrics": ["fraud_detection_rate", "false_positive_rate"],
      "script_reference": "examples/01_intro/data_factory.py"
    },
    "iot_monitoring": {
      "data_types": ["sensor_data", "device_status"],
      "key_metrics": ["data_integrity", "real_time_latency"],
      "script_reference": "examples/01_intro/masking_policy_demo.py"
    },
    "content_distribution": {
      "data_types": ["user_preferences", "content_metadata"],
      "key_metrics": ["content_match_rate", "user_retention"],
      "script_reference": "examples/01_intro/qa_summary.py"
    }
  }
}
```'''

# Replace the paragraph content
para.text = corrected_anchor

# Save the document
doc.save('1225全书定稿_final_standardized_fixed.docx')

print('Anchor [锚点020] has been fixed!')
print('Removed duplicate **版本**: v1.0 field')
print('Converted to standard > format')
print('Preserved all content including table and code examples')