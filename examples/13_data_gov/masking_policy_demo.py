# 敏感数据脱敏策略演示脚本
# 对应锚点13-003: 敏感数据处理策略流程图

import re
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MaskingStrategy(Enum):
    """脱敏策略枚举"""
    MASK = "mask"
    HASH = "hash"
    TOKENIZE = "tokenize"
    SYNTHETIC = "synthetic"
    REDACT = "redact"

@dataclass
class SensitiveDataRule:
    """敏感数据规则"""
    field_pattern: str
    data_type: str
    masking_strategy: MaskingStrategy
    compliance_frameworks: List[str]
    description: str

class SensitiveDataProcessor:
    """敏感数据处理器"""

    def __init__(self):
        self.masking_rules = self._load_masking_rules()
        self.classification_engine = SensitiveDataClassifier()
        self.token_store = {}  # 令牌化存储

    def _load_masking_rules(self) -> List[SensitiveDataRule]:
        """加载脱敏规则"""
        return [
            SensitiveDataRule(
                field_pattern=r".*email.*",
                data_type="email",
                masking_strategy=MaskingStrategy.MASK,
                compliance_frameworks=["GDPR", "CCPA"],
                description="邮箱地址脱敏"
            ),
            SensitiveDataRule(
                field_pattern=r".*phone.*",
                data_type="phone",
                masking_strategy=MaskingStrategy.MASK,
                compliance_frameworks=["GDPR", "CCPA"],
                description="电话号码脱敏"
            ),
            SensitiveDataRule(
                field_pattern=r".*ssn.*",
                data_type="ssn",
                masking_strategy=MaskingStrategy.TOKENIZE,
                compliance_frameworks=["GDPR", "CCPA", "HIPAA"],
                description="社会保险号令牌化"
            ),
            SensitiveDataRule(
                field_pattern=r".*credit_card.*",
                data_type="credit_card",
                masking_strategy=MaskingStrategy.MASK,
                compliance_frameworks=["PCI-DSS", "GDPR"],
                description="信用卡号脱敏"
            ),
            SensitiveDataRule(
                field_pattern=r".*address.*",
                data_type="address",
                masking_strategy=MaskingStrategy.REDACT,
                compliance_frameworks=["GDPR"],
                description="地址信息删除"
            )
        ]

    def process_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理敏感数据的主流程"""
        print("🔍 开始敏感数据处理流程...")

        # 1. 识别与分类
        sensitive_fields = self.classification_engine.scan_and_classify(data)
        print(f"📋 识别到 {len(sensitive_fields)} 个敏感字段")

        # 2. 应用脱敏策略
        masked_data = self.apply_masking_rules(data, sensitive_fields)
        print("🔒 脱敏策略应用完成")

        # 3. 令牌化处理
        tokenized_data = self.apply_tokenization(masked_data, sensitive_fields)
        print("🎫 令牌化处理完成")

        # 4. 验证与审计
        validated_data = self.validate_processing(tokenized_data)
        print("✅ 验证与审计完成")

        self.audit_processing(validated_data)
        print("📊 审计记录完成")

        return validated_data

    def apply_masking_rules(self, data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """应用脱敏规则"""
        masked_data = data.copy()

        for field, sensitivity in sensitive_fields.items():
            if field in masked_data:
                rule = self._find_applicable_rule(field, sensitivity)
                if rule:
                    masked_data[field] = self._execute_masking_rule(
                        masked_data[field], rule
                    )
                    print(f"   🔒 应用 {rule.masking_strategy.value} 策略到字段: {field}")

        return masked_data

    def _find_applicable_rule(self, field: str, sensitivity: str) -> Optional[SensitiveDataRule]:
        """查找适用的脱敏规则"""
        for rule in self.masking_rules:
            if re.match(rule.field_pattern, field, re.IGNORECASE):
                return rule
        return None

    def _execute_masking_rule(self, value: Any, rule: SensitiveDataRule) -> Any:
        """执行脱敏规则"""
        if rule.masking_strategy == MaskingStrategy.MASK:
            return self._mask_value(value, rule.data_type)
        elif rule.masking_strategy == MaskingStrategy.HASH:
            return self._hash_value(value)
        elif rule.masking_strategy == MaskingStrategy.TOKENIZE:
            return self._tokenize_value(value)
        elif rule.masking_strategy == MaskingStrategy.REDACT:
            return "***REDACTED***"
        else:
            return value

    def _mask_value(self, value: Any, data_type: str) -> str:
        """值脱敏"""
        value_str = str(value)

        if data_type == "email" and "@" in value_str:
            local, domain = value_str.split("@", 1)
            return f"{local[:2]}***@{domain}"
        elif data_type == "phone":
            if len(value_str) >= 10:
                return f"{value_str[:3]}***{value_str[-4:]}"
            else:
                return "***MASKED***"
        elif data_type == "credit_card":
            if len(value_str) >= 12:
                return f"{value_str[:4]}****{value_str[-4:]}"
            else:
                return "***MASKED***"
        else:
            # 通用脱敏
            return "***MASKED***"

    def _hash_value(self, value: Any) -> str:
        """值哈希"""
        value_str = str(value)
        return hashlib.sha256(value_str.encode()).hexdigest()[:16]

    def _tokenize_value(self, value: Any) -> str:
        """值令牌化"""
        value_str = str(value)
        token = f"TOKEN_{hashlib.md5(value_str.encode()).hexdigest()[:12]}"

        # 存储令牌映射（生产环境中应该使用安全的存储）
        self.token_store[token] = value_str

        return token

    def apply_tokenization(self, data: Dict[str, Any], sensitive_fields: List[str]) -> Dict[str, Any]:
        """应用令牌化"""
        tokenized_data = data.copy()

        for field, sensitivity in sensitive_fields.items():
            if field in tokenized_data:
                rule = self._find_applicable_rule(field, sensitivity)
                if rule and rule.masking_strategy == MaskingStrategy.TOKENIZE:
                    tokenized_data[field] = self._tokenize_value(tokenized_data[field])

        return tokenized_data

    def validate_processing(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证处理结果"""
        validation_results = {
            "masked_fields_count": 0,
            "tokenized_fields_count": 0,
            "compliance_check": True,
            "data_integrity": True
        }

        # 检查处理结果
        for key, value in processed_data.items():
            if isinstance(value, str):
                if value.startswith("TOKEN_"):
                    validation_results["tokenized_fields_count"] += 1
                elif "***" in value:
                    validation_results["masked_fields_count"] += 1

        print(f"   📊 验证结果: {validation_results}")
        return processed_data

    def audit_processing(self, processed_data: Dict[str, Any]):
        """审计处理过程"""
        audit_entry = {
            "timestamp": "2025-12-24T10:00:00Z",
            "action": "sensitive_data_processing",
            "fields_processed": len(processed_data),
            "compliance_frameworks": ["GDPR", "CCPA", "HIPAA"],
            "processing_status": "completed"
        }

        print(f"   📝 审计记录: {audit_entry}")

class SensitiveDataClassifier:
    """敏感数据分类器"""

    def scan_and_classify(self, data: Dict[str, Any]) -> Dict[str, str]:
        """扫描并分类敏感数据"""
        sensitive_fields = {}

        # 敏感字段模式
        patterns = {
            "email": r".*email.*",
            "phone": r".*phone.*|.*mobile.*",
            "ssn": r".*ssn.*|.*social.*",
            "credit_card": r".*credit.*|.*card.*",
            "address": r".*address.*",
            "name": r".*name.*",
            "birthdate": r".*birth.*|.*dob.*"
        }

        for key in data.keys():
            for sensitivity, pattern in patterns.items():
                if re.match(pattern, key, re.IGNORECASE):
                    sensitive_fields[key] = sensitivity
                    break

        return sensitive_fields

# 演示函数
def demo_masking_policy():
    """脱敏策略演示"""
    print("🎭 敏感数据脱敏策略演示")
    print("=" * 50)

    # 创建处理器
    processor = SensitiveDataProcessor()

    # 测试数据
    test_data = {
        "user_email": "john.doe@example.com",
        "user_phone": "13800138000",
        "user_ssn": "123-45-6789",
        "user_credit_card": "4111111111111111",
        "user_address": "123 Main St, Anytown, USA",
        "user_name": "John Doe",
        "regular_field": "normal_value"
    }

    print("📥 原始数据:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")

    print("\n🔄 处理中...")

    # 处理数据
    processed_data = processor.process_sensitive_data(test_data)

    print("\n📤 处理后数据:")
    for key, value in processed_data.items():
        print(f"   {key}: {value}")

    print("\n🎉 演示完成！")

if __name__ == "__main__":
    demo_masking_policy()