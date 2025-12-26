#!/usr/bin/env python3
"""
数据脱敏/掩码策略示例脚本
用于演示如何实现数据脱敏和掩码策略

作者: 安全测试框架
版本: 1.0
更新时间: 2025-12-24
"""

import re
import hashlib
import random
import string
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MaskingRule:
    """脱敏规则定义"""
    field_name: str
    rule_type: str  # mask, hash, token, synthetic
    pattern: Optional[str] = None
    keep_chars: int = 0
    mask_char: str = '*'
    description: str = ''

@dataclass
class MaskingResult:
    """脱敏结果"""
    original_value: str
    masked_value: str
    rule_applied: str
    timestamp: datetime
    success: bool

class DataMaskingEngine:
    """数据脱敏引擎"""

    def __init__(self, rules_config: Dict[str, Any]):
        """
        初始化脱敏引擎

        Args:
            rules_config: 脱敏规则配置
        """
        self.rules = self._load_rules(rules_config)
        self.results = []

    def _load_rules(self, config: Dict[str, Any]) -> Dict[str, MaskingRule]:
        """加载脱敏规则"""
        rules = {}
        for rule_config in config.get('masking_rules', []):
            rule = MaskingRule(
                field_name=rule_config['field'],
                rule_type=rule_config['type'],
                pattern=rule_config.get('pattern'),
                keep_chars=rule_config.get('keep_chars', 0),
                mask_char=rule_config.get('mask_char', '*'),
                description=rule_config.get('description', '')
            )
            rules[rule.field_name] = rule
        return rules

    def apply_masking(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        应用脱敏规则到数据框

        Args:
            data: 原始数据框

        Returns:
            脱敏后的数据框
        """
        masked_data = data.copy()

        for column in masked_data.columns:
            if column in self.rules:
                rule = self.rules[column]
                logger.info(f"应用脱敏规则到列 '{column}': {rule.rule_type}")

                masked_data[column] = masked_data[column].apply(
                    lambda x: self._apply_single_rule(str(x), rule)
                )

        return masked_data

    def _apply_single_rule(self, value: str, rule: MaskingRule) -> str:
        """应用单个脱敏规则"""
        try:
            if rule.rule_type == 'mask':
                return self._mask_value(value, rule)
            elif rule.rule_type == 'hash':
                return self._hash_value(value)
            elif rule.rule_type == 'token':
                return self._tokenize_value(value)
            elif rule.rule_type == 'synthetic':
                return self._generate_synthetic(value, rule)
            else:
                logger.warning(f"未知规则类型: {rule.rule_type}")
                return value
        except Exception as e:
            logger.error(f"应用规则失败: {e}")
            return value

    def _mask_value(self, value: str, rule: MaskingRule) -> str:
        """掩码处理"""
        if not value:
            return value

        # 保留前N个字符
        keep = rule.keep_chars
        if keep > 0 and len(value) > keep:
            return value[:keep] + rule.mask_char * (len(value) - keep)
        else:
            # 全掩码
            return rule.mask_char * len(value)

    def _hash_value(self, value: str) -> str:
        """哈希处理"""
        if not value:
            return value

        # 使用SHA256哈希
        hash_obj = hashlib.sha256(value.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # 取前16位

    def _tokenize_value(self, value: str) -> str:
        """令牌化处理"""
        if not value:
            return value

        # 生成随机令牌
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"TOKEN_{token}"

    def _generate_synthetic(self, value: str, rule: MaskingRule) -> str:
        """生成合成数据"""
        if not value:
            return value

        # 根据模式生成合成数据
        if rule.pattern == 'phone':
            return self._generate_phone()
        elif rule.pattern == 'email':
            return self._generate_email()
        elif rule.pattern == 'id_card':
            return self._generate_id_card()
        else:
            # 默认生成随机字符串
            return ''.join(random.choices(string.ascii_letters + string.digits, k=len(value)))

    def _generate_phone(self) -> str:
        """生成合成手机号"""
        prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                   '150', '151', '152', '153', '155', '156', '157', '158', '159',
                   '170', '171', '172', '173', '174', '175', '176', '177', '178', '179']
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{suffix}"

    def _generate_email(self) -> str:
        """生成合成邮箱"""
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', '163.com', 'qq.com']
        name_length = random.randint(5, 10)
        name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=name_length))
        domain = random.choice(domains)
        return f"{name}@{domain}"

    def _generate_id_card(self) -> str:
        """生成合成身份证号"""
        # 简化的身份证生成逻辑
        provinces = ['11', '12', '13', '14', '15', '21', '22', '23', '31', '32', '33', '34', '35', '36', '37']
        province = random.choice(provinces)
        city = f"{random.randint(10, 99):02d}"
        county = f"{random.randint(100, 999):03d}"
        birth_year = str(random.randint(1950, 2005))
        birth_month = f"{random.randint(1, 12):02d}"
        birth_day = f"{random.randint(1, 28):02d}"
        sequence = f"{random.randint(100, 999):03d}"
        gender = random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

        id_without_check = f"{province}{city}{county}{birth_year}{birth_month}{birth_day}{sequence}{gender}"

        # 计算校验码（简化版）
        check_code = str(random.randint(0, 9))
        return f"{id_without_check}{check_code}"

    def validate_masking(self, original_data: pd.DataFrame, masked_data: pd.DataFrame) -> Dict[str, Any]:
        """验证脱敏效果"""
        validation_results = {}

        for column in original_data.columns:
            if column in self.rules:
                original_values = original_data[column].astype(str)
                masked_values = masked_data[column].astype(str)

                rule = self.rules[column]

                # 检查是否完全相同（不应该相同）
                identical_count = (original_values == masked_values).sum()
                identical_rate = identical_count / len(original_values)

                # 检查掩码字符使用
                mask_char_count = masked_values.str.count(re.escape(rule.mask_char)).sum()

                validation_results[column] = {
                    'rule_type': rule.rule_type,
                    'identical_rate': identical_rate,
                    'mask_char_count': mask_char_count,
                    'total_records': len(original_values),
                    'validation_passed': identical_rate < 0.1  # 相似率应小于10%
                }

        return validation_results

    def generate_report(self) -> Dict[str, Any]:
        """生成脱敏报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'rules_applied': len(self.rules),
            'rules_detail': [
                {
                    'field': rule.field_name,
                    'type': rule.rule_type,
                    'description': rule.description
                }
                for rule in self.rules.values()
            ],
            'summary': {
                'total_fields_processed': len(self.rules),
                'masking_types_used': list(set(rule.rule_type for rule in self.rules.values()))
            }
        }

        return report

# 使用示例
if __name__ == "__main__":
    # 示例配置
    config = {
        'masking_rules': [
            {
                'field': 'phone',
                'type': 'mask',
                'keep_chars': 3,
                'mask_char': '*',
                'description': '手机号掩码，保留前3位'
            },
            {
                'field': 'email',
                'type': 'token',
                'description': '邮箱令牌化'
            },
            {
                'field': 'id_card',
                'type': 'hash',
                'description': '身份证哈希'
            },
            {
                'field': 'name',
                'type': 'synthetic',
                'pattern': 'name',
                'description': '姓名合成'
            }
        ]
    }

    # 创建脱敏引擎
    engine = DataMaskingEngine(config)

    # 示例数据
    sample_data = pd.DataFrame({
        'name': ['张三', '李四', '王五'],
        'phone': ['13800138000', '13900139000', '13700137000'],
        'email': ['zhangsan@example.com', 'lisi@example.com', 'wangwu@example.com'],
        'id_card': ['110101199001011234', '120102199002022345', '130103199003033456']
    })

    print("原始数据:")
    print(sample_data)

    # 应用脱敏
    masked_data = engine.apply_masking(sample_data)

    print("\n脱敏后数据:")
    print(masked_data)

    # 验证脱敏效果
    validation = engine.validate_masking(sample_data, masked_data)
    print("\n验证结果:")
    for field, result in validation.items():
        print(f"{field}: 相似率={result['identical_rate']:.2%}, 验证通过={result['validation_passed']}")

    # 生成报告
    report = engine.generate_report()
    print(f"\n脱敏报告: 处理了 {report['summary']['total_fields_processed']} 个字段")