# Test Case Management Module
# Handles test case lifecycle, organization, and execution

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TestCaseMetadata:
    """Test case metadata"""
    id: str
    name: str
    description: str
    type: str
    tags: List[str]
    priority: str
    author: str
    created_at: str
    updated_at: str
    dependencies: List[str]
    parameters: Dict[str, Any]
    assertions: List[Dict[str, Any]]

class TestCaseManager:
    """Manages test cases lifecycle"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.test_cases: Dict[str, TestCaseMetadata] = {}

    def load_test_cases(self):
        """Load all test cases from repository"""
        test_case_files = self.base_path.glob("**/*.yml")

        for file_path in test_case_files:
            if file_path.name.startswith('test_case_'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    case_data = yaml.safe_load(f)

                test_case = TestCaseMetadata(**case_data)
                self.test_cases[test_case.id] = test_case

    def get_test_case(self, case_id: str) -> Optional[TestCaseMetadata]:
        """Get test case by ID"""
        return self.test_cases.get(case_id)

    def get_test_cases_by_tag(self, tag: str) -> List[TestCaseMetadata]:
        """Get test cases by tag"""
        return [tc for tc in self.test_cases.values() if tag in tc.tags]

    def get_test_cases_by_type(self, case_type: str) -> List[TestCaseMetadata]:
        """Get test cases by type"""
        return [tc for tc in self.test_cases.values() if tc.type == case_type]

    def validate_dependencies(self, case_id: str) -> List[str]:
        """Validate test case dependencies"""
        case = self.get_test_case(case_id)
        if not case:
            return [f"Test case {case_id} not found"]

        missing_deps = []
        for dep_id in case.dependencies:
            if dep_id not in self.test_cases:
                missing_deps.append(dep_id)

        return missing_deps

    def create_test_case(self, metadata: TestCaseMetadata):
        """Create new test case"""
        metadata.created_at = datetime.now().isoformat()
        metadata.updated_at = metadata.created_at

        self.test_cases[metadata.id] = metadata
        self._save_test_case(metadata)

    def update_test_case(self, case_id: str, updates: Dict[str, Any]):
        """Update existing test case"""
        if case_id not in self.test_cases:
            raise ValueError(f"Test case {case_id} not found")

        case = self.test_cases[case_id]
        for key, value in updates.items():
            if hasattr(case, key):
                setattr(case, key, value)

        case.updated_at = datetime.now().isoformat()
        self._save_test_case(case)

    def _save_test_case(self, test_case: TestCaseMetadata):
        """Save test case to file"""
        file_path = self.base_path / f"test_case_{test_case.id}.yml"

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(test_case), f, default_flow_style=False, allow_unicode=True)

class TestSuite:
    """Test suite for organizing test cases"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.test_cases: List[str] = []
        self.setup_steps: List[Dict[str, Any]] = []
        self.teardown_steps: List[Dict[str, Any]] = []

    def add_test_case(self, case_id: str):
        """Add test case to suite"""
        if case_id not in self.test_cases:
            self.test_cases.append(case_id)

    def remove_test_case(self, case_id: str):
        """Remove test case from suite"""
        if case_id in self.test_cases:
            self.test_cases.remove(case_id)

    def set_setup_steps(self, steps: List[Dict[str, Any]]):
        """Set test suite setup steps"""
        self.setup_steps = steps

    def set_teardown_steps(self, steps: List[Dict[str, Any]]):
        """Set test suite teardown steps"""
        self.teardown_steps = steps

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'test_cases': self.test_cases,
            'setup_steps': self.setup_steps,
            'teardown_steps': self.teardown_steps
        }

# Example test case YAML structure
EXAMPLE_TEST_CASE = """
id: data_quality_check_001
name: "用户数据质量校验"
description: "校验用户表数据质量，包括完整性、准确性、一致性"
type: quality
tags:
  - daily
  - critical
  - user_data
priority: high
author: qa_team
created_at: "2025-12-23T10:00:00Z"
updated_at: "2025-12-23T10:00:00Z"
dependencies: []
parameters:
  table_name: user_table
  sample_size: 10000
  check_date: "2025-12-23"
assertions:
  - type: completeness
    field: user_id
    threshold: 0.99
  - type: uniqueness
    field: user_id
    threshold: 1.0
  - type: format
    field: email
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
"""

if __name__ == "__main__":
    # Initialize test case manager
    manager = TestCaseManager("test_cases/")

    # Load existing test cases
    manager.load_test_cases()

    print(f"Loaded {len(manager.test_cases)} test cases")

    # Example: Get test cases by tag
    daily_tests = manager.get_test_cases_by_tag("daily")
    print(f"Found {len(daily_tests)} daily test cases")

    # Example: Validate dependencies
    for case_id in manager.test_cases.keys():
        missing_deps = manager.validate_dependencies(case_id)
        if missing_deps:
            print(f"Test case {case_id} has missing dependencies: {missing_deps}")