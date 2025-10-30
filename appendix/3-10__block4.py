import os
import re
import json
import logging
import hashlib
import secrets
import numpy as np
import pandas as pd
import random
from typing import Dict, List, Any, Optional, Union, Callable, Pattern
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   filename='sensitive_data_protection.log')
logger = logging.getLogger(__name__)

class SensitiveDataIdentifier:
    """敏感数据识别器"""
    
    def __init__(self, config_path: str = 'sensitive_data_config.json'):
        self.config = self._load_config(config_path)
        self._init_patterns()
        self._init_models()
        logger.info("敏感数据识别器初始化完成")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            'sensitive_data_types': {
                'phone': {
                    'description': '手机号码',
                    'patterns': [r'1[3-9]\d{9}'],
                    'confidence_threshold': 0.9
                },
                'id_card': {
                    'description': '身份证号',
                    'patterns': [r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]'],
                    'confidence_threshold': 0.95
                },
                'email': {
                    'description': '电子邮箱',
                    'patterns': [r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'],
                    'confidence_threshold': 0.9
                },
                'bank_card': {
                    'description': '银行卡号',
                    'patterns': [r'[3-9]\d{12,18}'],
                    'confidence_threshold': 0.85,
                    'validator': 'luhn'
                },
                'name': {
                    'description': '姓名',
                    'keywords': ['先生', '女士', '小姐', '同志'],
                    'confidence_threshold': 0.7
                },
                'address': {
                    'description': '地址',
                    'keywords': ['省', '市', '区', '县', '街', '路', '道', '巷', '弄', '村', '号'],
                    'confidence_threshold': 0.75
                }
            },
            'keyword_dictionaries': {
                'sensitive_words': ['密码', '密钥', 'token', 'secret', '机密', '绝密']
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并默认配置和用户配置
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
        
        return default_config
    
    def _init_patterns(self):
        """初始化正则表达式模式"""
        self.patterns: Dict[str, List[Pattern]] = {}
        
        for data_type, config in self.config['sensitive_data_types'].items():
            if 'patterns' in config:
                self.patterns[data_type] = [re.compile(pattern) for pattern in config['patterns']]
            else:
                self.patterns[data_type] = []
    
    def _init_models(self):
        """初始化机器学习模型"""
        # 创建一个简单的文本分类模型用于敏感内容检测
        self.text_classifier = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)),
            ('clf', MultinomialNB())
        ])
        
        # 这里可以添加模型训练的代码
        # 在实际应用中，应该使用标注的训练数据来训练模型
    
    def _validate_bank_card(self, card_number: str) -> bool:
        """使用Luhn算法验证银行卡号"""
        # 移除空格和连字符
        card_number = card_number.replace(' ', '').replace('-', '')
        
        if not card_number.isdigit():
            return False
        
        # Luhn算法实现
        digits = [int(d) for d in card_number]
        checksum = 0
        
        # 从右向左遍历
        for i in range(len(digits) - 1, -1, -1):
            digit = digits[i]
            
            # 每隔一位数字乘以2
            if (len(digits) - i) % 2 == 0:
                digit *= 2
                # 如果乘以2后大于9，则减去9
                if digit > 9:
                    digit -= 9
            
            checksum += digit
        
        return checksum % 10 == 0
    
    def identify_in_text(self, text: str) -> List[Dict[str, Any]]:
        """识别文本中的敏感数据"""
        results = []
        
        # 基于正则表达式的识别
        for data_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    start, end = match.span()
                    value = match.group()
                    
                    # 检查是否需要额外验证
                    config = self.config['sensitive_data_types'][data_type]
                    is_valid = True
                    
                    if 'validator' in config:
                        if config['validator'] == 'luhn':
                            is_valid = self._validate_bank_card(value)
                    
                    if is_valid:
                        results.append({
                            'type': data_type,
                            'value': value,
                            'start': start,
                            'end': end,
                            'confidence': config.get('confidence_threshold', 0.8),
                            'method': 'pattern'
                        })
        
        # 基于关键词的识别
        for data_type, config in self.config['sensitive_data_types'].items():
            if 'keywords' in config:
                for keyword in config['keywords']:
                    for match in re.finditer(re.escape(keyword), text):
                        # 尝试提取关键词附近的内容作为敏感数据
                        context_start = max(0, match.start() - 20)
                        context_end = min(len(text), match.end() + 20)
                        context = text[context_start:context_end]
                        
                        results.append({
                            'type': data_type,
                            'value': context,
                            'start': context_start,
                            'end': context_end,
                            'confidence': config.get('confidence_threshold', 0.7),
                            'method': 'keyword'
                        })
        
        # 敏感词检测
        for word in self.config['keyword_dictionaries'].get('sensitive_words', []):
            if word in text:
                results.append({
                    'type': 'sensitive_word',
                    'value': word,
                    'confidence': 0.85,
                    'method': 'keyword_list'
                })
        
        return results
    
    def identify_in_dataframe(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """识别DataFrame中的敏感数据"""
        results = {}
        
        for column in df.columns:
            column_results = []
            
            # 对每列数据进行识别
            for idx, value in enumerate(df[column]):
                if pd.notna(value):
                    text = str(value)
                    identified = self.identify_in_text(text)
                    
                    for item in identified:
                        item['column'] = column
                        item['row'] = idx
                        column_results.append(item)
            
            if column_results:
                results[column] = column_results
        
        return results
    
    def identify_in_file(self, file_path: str) -> List[Dict[str, Any]]:
        """识别文件中的敏感数据"""
        results = []
        
        try:
            # 根据文件类型选择不同的处理方法
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.txt', '.log', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_number = 0
                    for line in f:
                        line_number += 1
                        identified = self.identify_in_text(line)
                        
                        for item in identified:
                            item['file_path'] = file_path
                            item['line_number'] = line_number
                            results.append(item)
            
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                file_results = self.identify_in_dataframe(df)
                
                for column, items in file_results.items():
                    for item in items:
                        item['file_path'] = file_path
                        results.append(item)
            
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 递归搜索JSON数据
                def search_json(obj, path=''):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            new_path = f"{path}.{key}" if path else key
                            if isinstance(value, str):
                                identified = self.identify_in_text(value)
                                for item in identified:
                                    item['file_path'] = file_path
                                    item['json_path'] = new_path
                                    results.append(item)
                            else:
                                search_json(value, new_path)
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            new_path = f"{path}[{i}]"
                            if isinstance(item, str):
                                identified = self.identify_in_text(item)
                                for sub_item in identified:
                                    sub_item['file_path'] = file_path
                                    sub_item['json_path'] = new_path
                                    results.append(sub_item)
                            else:
                                search_json(item, new_path)
                
                search_json(data)
            
            logger.info(f"已完成文件 {file_path} 的敏感数据识别，发现 {len(results)} 处敏感信息")
        except Exception as e:
            logger.error(f"识别文件中的敏感数据失败: {file_path}, 错误: {e}")
        
        return results

class DataMaskingEngine:
    """数据脱敏引擎"""
    
    def __init__(self):
        self.masking_methods = {
            'mask': self._mask,
            'replace': self._replace,
            'hash': self._hash,
            'shuffle': self._shuffle,
            'nullify': self._nullify,
            'encrypt': self._encrypt,
            'tokenize': self._tokenize
        }
        
        # 初始化掩码规则
        self.mask_rules = {
            'phone': self._mask_phone,
            'id_card': self._mask_id_card,
            'email': self._mask_email,
            'name': self._mask_name,
            'bank_card': self._mask_bank_card,
            'address': self._mask_address
        }
        
        # 替换映射表
        self.replacement_maps = {
            'name': ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十'],
            'city': ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉']
        }
        
        # 令牌化映射表
        self.token_map: Dict[str, str] = {}
        self.reverse_token_map: Dict[str, str] = {}
        
        logger.info("数据脱敏引擎初始化完成")
    
    def _mask(self, data: str, mask_char: str = '*', keep_prefix: int = 0, keep_suffix: int = 0) -> str:
        """基本掩码方法"""
        if len(data) <= keep_prefix + keep_suffix:
            return data
        
        masked_length = len(data) - keep_prefix - keep_suffix
        return data[:keep_prefix] + mask_char * masked_length + data[-keep_suffix:]
    
    def _mask_phone(self, phone: str) -> str:
        """掩码手机号"""
        return self._mask(phone, keep_prefix=3, keep_suffix=4)
    
    def _mask_id_card(self, id_card: str) -> str:
        """掩码身份证号"""
        return self._mask(id_card, keep_prefix=6, keep_suffix=4)
    
    def _mask_email(self, email: str) -> str:
        """掩码邮箱"""
        parts = email.split('@')
        if len(parts) != 2:
            return email
        
        username = parts[0]
        domain = parts[1]
        
        if len(username) <= 2:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = username[:2] + '*' * (len(username) - 2)
        
        return masked_username + '@' + domain
    
    def _mask_name(self, name: str) -> str:
        """掩码姓名"""
        if len(name) <= 1:
            return name
        elif len(name) == 2:
            return name[0] + '*'
        else:
            return name[0] + '*' * (len(name) - 2) + name[-1]
    
    def _mask_bank_card(self, bank_card: str) -> str:
        """掩码银行卡号"""
        # 移除空格和连字符
        bank_card = bank_card.replace(' ', '').replace('-', '')
        return self._mask(bank_card, keep_prefix=4, keep_suffix=4)
    
    def _mask_address(self, address: str) -> str:
        """掩码地址"""
        if len(address) <= 10:
            return address[:5] + '*' * (len(address) - 5)
        else:
            return address[:6] + '*' * (len(address) - 10) + address[-4:]
    
    def _replace(self, data: str, replacement_type: str = None) -> str:
        """替换敏感数据"""
        if replacement_type and replacement_type in self.replacement_maps:
            return random.choice(self.replacement_maps[replacement_type])
        
        # 随机生成替换值
        if data.isdigit():
            # 生成相同长度的随机数字
            return ''.join(random.choices('0123456789', k=len(data)))
        elif data.isalpha():
            # 生成相同长度的随机字母
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=len(data)))
        else:
            # 生成相同长度的随机字符
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=len(data)))
    
    def _hash(self, data: str, salt: Optional[str] = None) -> str:
        """哈希处理"""
        if salt is None:
            salt = secrets.token_hex(8)
        
        salted_data = (data + salt).encode('utf-8')
        hashed = hashlib.sha256(salted_data).hexdigest()
        return hashed[:16]  # 返回简短的哈希值
    
    def _shuffle(self, data: str) -> str:
        """随机打乱字符顺序"""
        chars = list(data)
        random.shuffle(chars)
        return ''.join(chars)
    
    def _nullify(self, data: str) -> str:
        """置空处理"""
        return 'NULL'
    
    def _encrypt(self, data: str, key: str = 'default_key') -> str:
        """简单加密处理（实际应用中应使用强加密算法）"""
        # 这里使用一个简单的XOR加密作为示例
        # 实际应用中应该使用如Fernet等安全的加密算法
        result = []
        for i in range(len(data)):
            char_code = ord(data[i]) ^ ord(key[i % len(key)])
            result.append(f"{char_code:02x}")
        return ''.join(result)
    
    def _tokenize(self, data: str, token_length: int = 16) -> str:
        """令牌化处理"""
        if data in self.token_map:
            return self.token_map[data]
        
        # 生成唯一令牌
        token = secrets.token_hex(token_length // 2)
        self.token_map[data] = token
        self.reverse_token_map[token] = data
        
        return token
    
    def mask_data(self, data: str, data_type: str, method: str = 'mask', **kwargs) -> str:
        """根据数据类型和方法进行脱敏"""
        # 如果有特定类型的掩码规则，优先使用
        if data_type in self.mask_rules and method == 'mask':
            return self.mask_rules[data_type](data)
        
        # 使用指定的掩码方法
        if method in self.masking_methods:
            return self.masking_methods[method](data, **kwargs)
        
        logger.warning(f"未知的脱敏方法: {method}")
        return data
    
    def mask_text(self, text: str, identified_items: List[Dict[str, Any]], method_map: Optional[Dict[str, str]] = None) -> str:
        """对文本中的敏感数据进行脱敏"""
        if not identified_items:
            return text
        
        if method_map is None:
            method_map = {}
        
        # 按位置降序排序，从后往前替换，避免位置偏移
        sorted_items = sorted(identified_items, key=lambda x: x['start'], reverse=True)
        masked_text = text
        
        for item in sorted_items:
            data_type = item['type']
            start = item['start']
            end = item['end']
            original_value = masked_text[start:end]
            
            # 获取该数据类型对应的脱敏方法
            method = method_map.get(data_type, 'mask')
            
            # 执行脱敏
            masked_value = self.mask_data(original_value, data_type, method)
            
            # 替换文本中的敏感数据
            masked_text = masked_text[:start] + masked_value + masked_text[end:]
        
        return masked_text
    
    def mask_dataframe(self, df: pd.DataFrame, identified_results: Dict[str, List[Dict[str, Any]]], 
                      method_map: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """对DataFrame中的敏感数据进行脱敏"""
        masked_df = df.copy()
        
        if method_map is None:
            method_map = {}
        
        for column, items in identified_results.items():
            if column not in masked_df.columns:
                continue
            
            # 按行号分组
            items_by_row = {}
            for item in items:
                row = item.get('row', 0)
                if row not in items_by_row:
                    items_by_row[row] = []
                items_by_row[row].append(item)
            
            # 对每行数据进行脱敏
            for row, row_items in items_by_row.items():
                if row >= len(masked_df):
                    continue
                
                value = str(masked_df.at[row, column])
                masked_value = self.mask_text(value, row_items, method_map)
                masked_df.at[row, column] = masked_value
        
        return masked_df
    
    def mask_file(self, file_path: str, output_path: Optional[str] = None, 
                 identifier: Optional[SensitiveDataIdentifier] = None, 
                 method_map: Optional[Dict[str, str]] = None) -> str:
        """对文件中的敏感数据进行脱敏"""
        if output_path is None:
            output_path = file_path + '.masked'
        
        if identifier is None:
            identifier = SensitiveDataIdentifier()
        
        if method_map is None:
            method_map = {}
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.txt', '.log']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 识别敏感数据
                identified = identifier.identify_in_text(content)
                
                # 脱敏
                masked_content = self.mask_text(content, identified, method_map)
                
                # 保存结果
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(masked_content)
            
            elif ext == '.csv':
                df = pd.read_csv(file_path)
                identified = identifier.identify_in_dataframe(df)
                masked_df = self.mask_dataframe(df, identified, method_map)
                masked_df.to_csv(output_path, index=False, encoding='utf-8')
            
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
                identified = identifier.identify_in_dataframe(df)
                masked_df = self.mask_dataframe(df, identified, method_map)
                masked_df.to_excel(output_path, index=False)
            
            logger.info(f"文件已脱敏: {file_path} -> {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"脱敏文件失败: {file_path}, 错误: {e}")
            raise

class DataMaskingValidator:
    """数据脱敏验证器"""
    
    def __init__(self):
        self.identifier = SensitiveDataIdentifier()
        logger.info("数据脱敏验证器初始化完成")
    
    def validate_effectiveness(self, original_data: str, masked_data: str) -> Dict[str, Any]:
        """验证脱敏效果"""
        # 识别原始数据中的敏感信息
        original_identified = self.identifier.identify_in_text(original_data)
        
        # 识别脱敏后数据中的敏感信息
        masked_identified = self.identifier.identify_in_text(masked_data)
        
        # 计算脱敏成功率
        original_count = len(original_identified)
        masked_count = len(masked_identified)
        
        success_rate = 1.0
        if original_count > 0:
            # 计算未被脱敏的敏感数据数量
            unmasked_count = 0
            for original_item in original_identified:
                for masked_item in masked_identified:
                    if original_item['type'] == masked_item['type']:
                        # 检查是否是相同的敏感数据
                        original_value = original_data[original_item['start']:original_item['end']]
                        masked_value = masked_data[masked_item['start']:masked_item['end']]
                        if original_value == masked_value:
                            unmasked_count += 1
                            break
            
            success_rate = (original_count - unmasked_count) / original_count
        
        return {
            'original_sensitive_count': original_count,
            'masked_sensitive_count': masked_count,
            'success_rate': success_rate,
            'is_effective': success_rate >= 0.95,  # 95%以上的成功率认为有效
            'original_identified_types': set(item['type'] for item in original_identified),
            'masked_identified_types': set(item['type'] for item in masked_identified)
        }
    
    def validate_consistency(self, original_data: str, masked_data: str) -> Dict[str, Any]:
        """验证脱敏后的数据一致性（保持格式、长度等）"""
        # 检查数据类型是否一致
        data_type_consistent = isinstance(original_data, type(masked_data))
        
        # 检查字符串长度是否合理
        length_ratio = len(masked_data) / len(original_data) if len(original_data) > 0 else 0
        length_reasonable = 0.5 <= length_ratio <= 2.0  # 长度在原始的0.5-2倍之间认为合理
        
        # 检查数值范围是否合理（如果都是数字）
        numeric_consistent = True
        if original_data.isdigit() and masked_data.isdigit():
            original_num = int(original_data)
            masked_num = int(masked_data)
            # 对于ID类数字，不要求数值接近，只要求位数合理
            numeric_consistent = len(original_data) == len(masked_data)
        
        # 检查格式特征是否保留
        format_preserved = False
        if any(pattern in masked_data for pattern in ['.', '@', '-', '_']):
            format_preserved = True
        
        return {
            'data_type_consistent': data_type_consistent,
            'length_reasonable': length_reasonable,
            'numeric_consistent': numeric_consistent,
            'format_preserved': format_preserved,
            'is_consistent': data_type_consistent and length_reasonable
        }
    
    def validate_irreversibility(self, masked_data: str, original_data: Optional[str] = None) -> Dict[str, Any]:
        """验证脱敏的不可逆性"""
        # 检查是否可以从脱敏数据中直接提取原始信息
        contains_original_info = False
        if original_data:
            contains_original_info = any(substr in masked_data for substr in original_data.split())
        
        # 检查掩码覆盖率
        mask_ratio = masked_data.count('*') / len(masked_data) if len(masked_data) > 0 else 0
        high_mask_coverage = mask_ratio > 0.5
        
        # 检查是否使用了不可逆的脱敏方法
        uses_irreversible_method = any(method in masked_data.lower() for method in ['hash', 'null'])
        
        return {
            'contains_original_info': contains_original_info,
            'mask_ratio': mask_ratio,
            'high_mask_coverage': high_mask_coverage,
            'uses_irreversible_method': uses_irreversible_method,
            'is_irreversible': not contains_original_info and (high_mask_coverage or uses_irreversible_method)
        }
    
    def validate_dataframe(self, original_df: pd.DataFrame, masked_df: pd.DataFrame) -> Dict[str, Any]:
        """验证DataFrame脱敏效果"""
        # 检查列结构是否一致
        columns_consistent = list(original_df.columns) == list(masked_df.columns)
        
        # 检查行数是否一致
        rows_consistent = len(original_df) == len(masked_df)
        
        # 检查数据类型是否一致
        dtypes_consistent = True
        for column in original_df.columns:
            if column in masked_df.columns:
                if str(original_df[column].dtype) != str(masked_df[column].dtype):
                    dtypes_consistent = False
                    break
        
        # 验证每列的脱敏效果
        column_results = {}
        for column in original_df.columns:
            if column not in masked_df.columns:
                continue
            
            effectiveness_scores = []
            for idx in range(len(original_df)):
                if idx < len(masked_df):
                    original_val = str(original_df.at[idx, column])
                    masked_val = str(masked_df.at[idx, column])
                    
                    effectiveness = self.validate_effectiveness(original_val, masked_val)
                    effectiveness_scores.append(effectiveness['success_rate'])
            
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 1.0
            column_results[column] = avg_effectiveness
        
        overall_effectiveness = sum(column_results.values()) / len(column_results) if column_results else 1.0
        
        return {
            'columns_consistent': columns_consistent,
            'rows_consistent': rows_consistent,
            'dtypes_consistent': dtypes_consistent,
            'column_effectiveness': column_results,
            'overall_effectiveness': overall_effectiveness,
            'is_valid': columns_consistent and rows_consistent and overall_effectiveness >= 0.9
        }
    
    def generate_validation_report(self, original_data: Any, masked_data: Any, 
                                 data_type: str = 'text') -> Dict[str, Any]:
        """生成完整的验证报告"""
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'data_type': data_type
        }
        
        if data_type == 'text':
            effectiveness = self.validate_effectiveness(original_data, masked_data)
            consistency = self.validate_consistency(original_data, masked_data)
            irreversibility = self.validate_irreversibility(masked_data, original_data)
            
            report.update({
                'effectiveness': effectiveness,
                'consistency': consistency,
                'irreversibility': irreversibility,
                'overall_valid': effectiveness['is_effective'] and consistency['is_consistent'] and irreversibility['is_irreversible']
            })
        
        elif data_type == 'dataframe':
            df_validation = self.validate_dataframe(original_data, masked_data)
            report['dataframe_validation'] = df_validation
            report['overall_valid'] = df_validation['is_valid']
        
        return report
    
    def visualize_validation_results(self, report: Dict[str, Any], output_path: str = 'validation_report.png'):
        """可视化验证结果"""
        try:
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            # 有效性可视化
            effectiveness = report.get('effectiveness', {})
            effectiveness_score = effectiveness.get('success_rate', 0)
            axes[0].pie([effectiveness_score, 1 - effectiveness_score], 
                       labels=['脱敏成功', '脱敏失败'], 
                       autopct='%1.1f%%',
                       colors=['#4CAF50', '#F44336'])
            axes[0].set_title('脱敏有效性')
            
            # 一致性可视化
            consistency = report.get('consistency', {})
            consistency_metrics = {
                '数据类型一致': consistency.get('data_type_consistent', False),
                '长度合理': consistency.get('length_reasonable', False),
                '数值一致': consistency.get('numeric_consistent', False),
                '格式保留': consistency.get('format_preserved', False)
            }
            
            consistency_values = [1 if v else 0 for v in consistency_metrics.values()]
            axes[1].bar(consistency_metrics.keys(), consistency_values, color=['#2196F3', '#FF9800'])
            axes[1].set_ylim(0, 1.2)
            axes[1].set_title('数据一致性')
            for i, v in enumerate(consistency_values):
                axes[1].text(i, v + 0.1, '是' if v else '否', ha='center')
            
            # 不可逆性可视化
            irreversibility = report.get('irreversibility', {})
            mask_ratio = irreversibility.get('mask_ratio', 0)
            axes[2].bar(['掩码覆盖率'], [mask_ratio], color='#9C27B0')
            axes[2].set_ylim(0, 1)
            axes[2].set_title('不可逆性')
            axes[2].text(0, mask_ratio + 0.05, f'{mask_ratio:.1%}', ha='center')
            
            plt.tight_layout()
            plt.savefig(output_path)
            logger.info(f"验证结果可视化已保存至: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"生成可视化结果失败: {e}")
            return None

class SensitiveDataProtectionTestSuite:
    """敏感数据保护测试套件"""
    
    def __init__(self):
        self.identifier = SensitiveDataIdentifier()
        self.masker = DataMaskingEngine()
        self.validator = DataMaskingValidator()
        self.test_results = []
        logger.info("敏感数据保护测试套件初始化完成")
    
    def test_data_identification(self, test_data: str, expected_types: List[str]) -> Dict[str, Any]:
        """测试敏感数据识别功能"""
        identified = self.identifier.identify_in_text(test_data)
        identified_types = set(item['type'] for item in identified)
        expected_set = set(expected_types)
        
        # 计算准确率和召回率
        true_positives = len(identified_types.intersection(expected_set))
        false_positives = len(identified_types - expected_set)
        false_negatives = len(expected_set - identified_types)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        result = {
            'test_type': 'data_identification',
            'test_data': test_data[:100] + '...' if len(test_data) > 100 else test_data,
            'expected_types': expected_types,
            'identified_types': list(identified_types),
            'identified_count': len(identified),
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'passed': f1_score >= 0.9
        }
        
        self.test_results.append(result)
        logger.info(f"数据识别测试完成: 精度={precision:.2f}, 召回={recall:.2f}, F1={f1_score:.2f}, 通过={result['passed']}")
        return result
    
    def test_data_masking(self, test_data: str, data_type: str, method: str = 'mask') -> Dict[str, Any]:
        """测试数据脱敏功能"""
        masked_data = self.masker.mask_data(test_data, data_type, method)
        
        # 验证脱敏效果
        validation = self.validator.generate_validation_report(test_data, masked_data)
        
        result = {
            'test_type': 'data_masking',
            'original_data': test_data,
            'masked_data': masked_data,
            'data_type': data_type,
            'masking_method': method,
            'validation': validation,
            'passed': validation['overall_valid']
        }
        
        self.test_results.append(result)
        logger.info(f"数据脱敏测试完成: 类型={data_type}, 方法={method}, 通过={result['passed']}")
        return result
    
    def test_comprehensive_protection(self, test_data: str, expected_types: List[str], 
                                    method_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试完整的敏感数据保护流程"""
        # 1. 识别敏感数据
        identified = self.identifier.identify_in_text(test_data)
        
        # 2. 执行脱敏
        masked_data = self.masker.mask_text(test_data, identified, method_map)
        
        # 3. 验证脱敏效果
        validation = self.validator.generate_validation_report(test_data, masked_data)
        
        # 4. 评估整体保护效果
        identified_types = set(item['type'] for item in identified)
        expected_set = set(expected_types)
        true_positives = len(identified_types.intersection(expected_set))
        false_negatives = len(expected_set - identified_types)
        
        detection_rate = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        result = {
            'test_type': 'comprehensive_protection',
            'original_data_sample': test_data[:200] + '...' if len(test_data) > 200 else test_data,
            'masked_data_sample': masked_data[:200] + '...' if len(masked_data) > 200 else masked_data,
            'identified_count': len(identified),
            'detection_rate': detection_rate,
            'protection_effectiveness': validation['effectiveness']['success_rate'],
            'validation': validation,
            'passed': detection_rate >= 0.9 and validation['overall_valid']
        }
        
        self.test_results.append(result)
        logger.info(f"综合保护测试完成: 检测率={detection_rate:.2f}, 保护效果={validation['effectiveness']['success_rate']:.2f}, 通过={result['passed']}")
        return result
    
    def test_file_protection(self, file_path: str, output_path: Optional[str] = None, 
                           method_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """测试文件脱敏功能"""
        if output_path is None:
            output_path = file_path + '.masked.test'
        
        try:
            # 执行文件脱敏
            masked_file = self.masker.mask_file(file_path, output_path, self.identifier, method_map)
            
            # 验证原始文件和脱敏文件
            original_size = os.path.getsize(file_path)
            masked_size = os.path.getsize(masked_file)
            
            # 检查脱敏后文件是否仍然可识别敏感信息
            masked_identified = self.identifier.identify_in_file(masked_file)
            
            result = {
                'test_type': 'file_protection',
                'file_path': file_path,
                'masked_file_path': masked_file,
                'original_size': original_size,
                'masked_size': masked_size,
                'size_change_ratio': masked_size / original_size,
                'remaining_sensitive_count': len(masked_identified),
                'passed': len(masked_identified) == 0 or len(masked_identified) < 5  # 允许少量误报
            }
            
            self.test_results.append(result)
            logger.info(f"文件保护测试完成: 文件={file_path}, 剩余敏感信息={len(masked_identified)}, 通过={result['passed']}")
            return result
        except Exception as e:
            logger.error(f"文件保护测试失败: {file_path}, 错误: {e}")
            return {
                'test_type': 'file_protection',
                'file_path': file_path,
                'error': str(e),
                'passed': False
            }
    
    def generate_test_report(self, output_path: str = 'sensitive_data_protection_report.json') -> str:
        """生成测试报告"""
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for r in self.test_results if r['passed']),
            'pass_rate': sum(1 for r in self.test_results if r['passed']) / len(self.test_results) if self.test_results else 0,
            'test_results': self.test_results
        }
        
        # 保存报告
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"测试报告已生成: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"生成测试报告失败: {e}")
            raise
    
    def visualize_test_results(self, output_path: str = 'test_results_summary.png'):
        """可视化测试结果摘要"""
        try:
            # 统计各类测试的结果
            test_types = {}
            for result in self.test_results:
                test_type = result['test_type']
                if test_type not in test_types:
                    test_types[test_type] = {'total': 0, 'passed': 0}
                test_types[test_type]['total'] += 1
                if result['passed']:
                    test_types[test_type]['passed'] += 1
            
            # 创建可视化
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 1. 整体通过率
            passed_count = sum(1 for r in self.test_results if r['passed'])
            failed_count = len(self.test_results) - passed_count
            ax1.pie([passed_count, failed_count], 
                   labels=['通过', '失败'], 
                   autopct='%1.1f%%',
                   colors=['#4CAF50', '#F44336'])
            ax1.set_title('整体测试结果')
            
            # 2. 各类测试通过率
            types = list(test_types.keys())
            pass_rates = [test_types[t]['passed'] / test_types[t]['total'] for t in types]
            
            bars = ax2.bar(types, pass_rates, color='#2196F3')
            ax2.set_ylim(0, 1.1)
            ax2.set_title('各类测试通过率')
            ax2.set_xticklabels(types, rotation=45, ha='right')
            
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.1%}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(output_path)
            logger.info(f"测试结果可视化已保存至: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"生成测试结果可视化失败: {e}")
            return None

# 使用示例
def main():
    print("=== 敏感数据保护测试框架演示 ===")
    
    # 创建测试套件
    test_suite = SensitiveDataProtectionTestSuite()
    
    # 1. 测试敏感数据识别
    print("\n=== 1. 测试敏感数据识别 ===")
    test_text = "联系电话: 13800138000, 邮箱: user123@example.com, 身份证号: 110101199001011234, 银行卡: 6222021234567890123"
    print(f"测试文本: {test_text}")
    
    expected_types = ['phone', 'email', 'id_card', 'bank_card']
    identification_result = test_suite.test_data_identification(test_text, expected_types)
    
    print(f"识别结果: {identification_result['identified_types']}")
    print(f"精度: {identification_result['precision']:.2f}, 召回: {identification_result['recall']:.2f}, F1: {identification_result['f1_score']:.2f}")
    print(f"测试{'通过' if identification_result['passed'] else '失败'}")
    
    # 2. 测试数据脱敏
    print("\n=== 2. 测试数据脱敏 ===")
    test_cases = [
        ('13800138000', 'phone'),
        ('110101199001011234', 'id_card'),
        ('user123@example.com', 'email'),
        ('张三', 'name'),
        ('6222021234567890123', 'bank_card')
    ]
    
    for original, data_type in test_cases:
        masking_result = test_suite.test_data_masking(original, data_type)
        print(f"{data_type}: {original} -> {masking_result['masked_data']} {'(通过)' if masking_result['passed'] else '(失败)'}")
    
    # 3. 测试综合保护
    print("\n=== 3. 测试综合保护 ===")
    method_map = {
        'phone': 'mask',
        'id_card': 'mask',
        'email': 'mask',
        'name': 'replace',
        'bank_card': 'hash'
    }
    
    comprehensive_result = test_suite.test_comprehensive_protection(test_text, expected_types, method_map)
    print(f"检测率: {comprehensive_result['detection_rate']:.2f}")
    print(f"保护效果: {comprehensive_result['protection_effectiveness']:.2f}")
    print(f"测试{'通过' if comprehensive_result['passed'] else '失败'}")
    
    # 4. 生成测试报告
    print("\n=== 4. 生成测试报告 ===")
    report_path = test_suite.generate_test_report()
    print(f"测试报告已生成: {report_path}")
    
    # 5. 可视化测试结果
    viz_path = test_suite.visualize_test_results()
    if viz_path:
        print(f"测试结果可视化已生成: {viz_path}")
    
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    main()
