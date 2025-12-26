# AI测试用例生成器

import openai
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AITestCaseGenerator:
    """AI测试用例生成器"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.generation_history = []

    def generate_test_cases_from_requirements(self, requirements: str,
                                            context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """从需求文档生成测试用例"""

        prompt = f"""
        分析以下需求文档，生成全面的测试用例。重点关注：
        1. 功能性测试用例（正常流程、边界条件、异常处理）
        2. 非功能性测试用例（性能、安全、可用性）
        3. 集成测试用例（与其他系统的交互）
        4. 用户体验测试用例（易用性、可访问性）

        需求文档：
        {requirements}

        上下文信息：{json.dumps(context, ensure_ascii=False) if context else ''}

        请以JSON格式返回测试用例列表，每个测试用例包含：
        - id: 唯一标识符
        - title: 测试用例标题
        - description: 详细描述
        - preconditions: 前置条件列表
        - steps: 测试步骤列表
        - expected_result: 期望结果
        - priority: 优先级 (high, medium, low)
        - category: 类别 (functional, security, performance, usability, integration)
        - tags: 相关标签列表

        {f'上下文信息：{json.dumps(context, ensure_ascii=False)}' if context else ''}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )

            result = response.choices[0].message.content
            test_cases = json.loads(result)

            logger.info(f"Generated {len(test_cases)} test cases from requirements")
            return test_cases

        except Exception as e:
            logger.error(f"Failed to generate test cases: {e}")
            return []

    def generate_test_cases_from_code(self, code: str, language: str = "python") -> List[Dict[str, Any]]:
        """从代码生成测试用例"""

        prompt = f"""
        分析以下{language}代码，生成单元测试用例。重点关注：
        1. 函数的各种输入场景
        2. 边界条件
        3. 异常处理
        4. 代码分支覆盖

        代码：
        ```{language}
        {code}
        ```

        请以JSON格式返回测试用例列表，每个测试用例包含：
        - function_name: 函数名
        - test_type: 测试类型
        - input_data: 输入数据
        - expected_output: 期望输出
        - description: 测试描述
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1500
            )

            result = response.choices[0].message.content
            test_cases = json.loads(result)

            logger.info(f"Generated {len(test_cases)} test cases from code")
            return test_cases

        except Exception as e:
            logger.error(f"Failed to generate test cases from code: {e}")
            return []

    def optimize_test_suite(self, existing_tests: List[Dict[str, Any]], coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """优化测试套件"""

        prompt = f"""
        基于现有的测试用例和覆盖率数据，优化测试套件。

        现有测试用例：
        {json.dumps(existing_tests[:10], ensure_ascii=False, indent=2)}  # 仅显示前10个

        覆盖率数据：
        {json.dumps(coverage_data, ensure_ascii=False, indent=2)}

        请提供优化建议：
        1. 识别冗余测试用例
        2. 发现覆盖率不足的区域
        3. 建议新增的测试用例
        4. 优化测试执行顺序

        以JSON格式返回优化结果。
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )

            result = response.choices[0].message.content
            optimization = json.loads(result)

            logger.info("Generated test suite optimization recommendations")
            return optimization

        except Exception as e:
            logger.error(f"Failed to optimize test suite: {e}")
            return {}

# 使用示例
if __name__ == "__main__":
    # 初始化生成器
    generator = AITestCaseGenerator(api_key="your-openai-api-key")

    # 示例需求文档
    requirements = """
    用户注册功能需求：
    1. 用户可以提供邮箱和密码进行注册
    2. 邮箱必须是有效格式
    3. 密码长度至少8位，包含字母和数字
    4. 相同邮箱不能重复注册
    5. 注册成功后发送确认邮件
    """

    # 生成测试用例
    test_cases = generator.generate_test_cases_from_requirements(requirements)

    print("生成的测试用例：")
    for tc in test_cases[:3]:  # 显示前3个
        print(f"- {tc.get('title', 'Unknown')}: {tc.get('description', '')}")

    # 示例代码
    sample_code = """
    def validate_email(email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def register_user(email: str, password: str) -> dict:
        if not validate_email(email):
            return {"success": False, "error": "Invalid email format"}

        if len(password) < 8 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            return {"success": False, "error": "Password too weak"}

        # 模拟用户注册逻辑
        return {"success": True, "user_id": "12345"}
    """

    # 从代码生成测试
    code_tests = generator.generate_test_cases_from_code(sample_code, "python")

    print("\n从代码生成的测试：")
    for ct in code_tests[:3]:  # 显示前3个
        print(f"- {ct.get('function_name', 'Unknown')}: {ct.get('description', '')}")