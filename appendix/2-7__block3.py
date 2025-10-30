# 大数据系统RBAC权限测试框架
import unittest
import json
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RBAC_Test_Framework')

class User:
    """用户类"""
    def __init__(self, user_id, username, roles=None):
        self.user_id = user_id
        self.username = username
        self.roles = roles or []
        self.attributes = {}
    
    def add_role(self, role):
        """添加角色"""
        if role not in self.roles:
            self.roles.append(role)
    
    def remove_role(self, role):
        """移除角色"""
        if role in self.roles:
            self.roles.remove(role)
    
    def set_attribute(self, name, value):
        """设置用户属性"""
        self.attributes[name] = value
    
    def get_attribute(self, name, default=None):
        """获取用户属性"""
        return self.attributes.get(name, default)

class Role:
    """角色类"""
    def __init__(self, role_id, role_name, permissions=None):
        self.role_id = role_id
        self.role_name = role_name
        self.permissions = permissions or []
        self.parent_roles = []
    
    def add_permission(self, permission):
        """添加权限"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission):
        """移除权限"""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def add_parent_role(self, parent_role):
        """添加父角色（用于权限继承）"""
        if parent_role not in self.parent_roles:
            self.parent_roles.append(parent_role)

class Permission:
    """权限类"""
    def __init__(self, permission_id, resource, action):
        self.permission_id = permission_id
        self.resource = resource  # 资源（如数据库表、API端点等）
        self.action = action      # 操作（如读、写、执行等）
    
    def __eq__(self, other):
        if not isinstance(other, Permission):
            return False
        return self.resource == other.resource and self.action == other.action
    
    def __hash__(self):
        return hash((self.resource, self.action))
    
    def __str__(self):
        return f"{self.resource}:{self.action}"

class RBACSystem:
    """RBAC系统模拟类"""
    def __init__(self):
        self.users = {}
        self.roles = {}
        self.permissions = {}
    
    def add_user(self, user):
        """添加用户"""
        self.users[user.user_id] = user
    
    def add_role(self, role):
        """添加角色"""
        self.roles[role.role_id] = role
    
    def add_permission(self, permission):
        """添加权限"""
        self.permissions[permission.permission_id] = permission
    
    def assign_role_to_user(self, user_id, role_id):
        """为用户分配角色"""
        if user_id in self.users and role_id in self.roles:
            self.users[user_id].add_role(self.roles[role_id])
            return True
        return False
    
    def revoke_role_from_user(self, user_id, role_id):
        """从用户撤销角色"""
        if user_id in self.users and role_id in self.roles:
            self.users[user_id].remove_role(self.roles[role_id])
            return True
        return False
    
    def grant_permission_to_role(self, role_id, permission_id):
        """为角色授予权限"""
        if role_id in self.roles and permission_id in self.permissions:
            self.roles[role_id].add_permission(self.permissions[permission_id])
            return True
        return False
    
    def revoke_permission_from_role(self, role_id, permission_id):
        """从角色撤销权限"""
        if role_id in self.roles and permission_id in self.permissions:
            self.roles[role_id].remove_permission(self.permissions[permission_id])
            return True
        return False
    
    def has_permission(self, user_id, resource, action):
        """检查用户是否有权限对资源执行操作（包括权限继承）"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        target_permission = Permission(None, resource, action)
        
        # 检查所有直接分配的角色及其父角色
        for role in user.roles:
            if self._check_role_permission(role, target_permission):
                return True
        
        return False
    
    def _check_role_permission(self, role, permission):
        """递归检查角色及其父角色是否拥有指定权限"""
        # 检查当前角色的直接权限
        if permission in role.permissions:
            return True
        
        # 递归检查父角色的权限
        for parent_role in role.parent_roles:
            if self._check_role_permission(parent_role, permission):
                return True
        
        return False
    
    def get_user_effective_permissions(self, user_id):
        """获取用户的有效权限列表（包括通过角色继承获得的权限）"""
        if user_id not in self.users:
            return []
        
        effective_permissions = set()
        user = self.users[user_id]
        
        def collect_permissions(role):
            for permission in role.permissions:
                effective_permissions.add(permission)
            for parent_role in role.parent_roles:
                collect_permissions(parent_role)
        
        for role in user.roles:
            collect_permissions(role)
        
        return list(effective_permissions)

class RBACSecurityTester(unittest.TestCase):
    """RBAC安全测试类"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建RBAC系统实例
        self.rbac = RBACSystem()
        
        # 创建权限
        self.rbac.add_permission(Permission(1, 'customer_data', 'read'))
        self.rbac.add_permission(Permission(2, 'customer_data', 'write'))
        self.rbac.add_permission(Permission(3, 'financial_data', 'read'))
        self.rbac.add_permission(Permission(4, 'financial_data', 'write'))
        self.rbac.add_permission(Permission(5, 'admin_panel', 'access'))
        
        # 创建角色
        self.rbac.add_role(Role(101, 'analyst'))
        self.rbac.add_role(Role(102, 'data_editor'))
        self.rbac.add_role(Role(103, 'admin'))
        
        # 创建角色继承关系
        self.rbac.roles[102].add_parent_role(self.rbac.roles[101])  # editor继承analyst权限
        self.rbac.roles[103].add_parent_role(self.rbac.roles[102])  # admin继承editor权限
        
        # 为角色分配权限
        self.rbac.grant_permission_to_role(101, 1)  # analyst可以读取customer_data
        self.rbac.grant_permission_to_role(101, 3)  # analyst可以读取financial_data
        self.rbac.grant_permission_to_role(102, 2)  # editor可以写入customer_data
        self.rbac.grant_permission_to_role(103, 4)  # admin可以写入financial_data
        self.rbac.grant_permission_to_role(103, 5)  # admin可以访问admin_panel
        
        # 创建用户
        self.rbac.add_user(User(1001, 'alice'))
        self.rbac.add_user(User(1002, 'bob'))
        self.rbac.add_user(User(1003, 'carol'))
        
        # 为用户分配角色
        self.rbac.assign_role_to_user(1001, 101)  # alice是analyst
        self.rbac.assign_role_to_user(1002, 102)  # bob是data_editor
        self.rbac.assign_role_to_user(1003, 103)  # carol是admin
    
    def test_direct_permission_assignment(self):
        """测试直接权限分配"""
        logger.info("开始测试直接权限分配")
        
        # Alice作为analyst应该只能读取客户数据
        self.assertTrue(self.rbac.has_permission(1001, 'customer_data', 'read'))
        self.assertFalse(self.rbac.has_permission(1001, 'customer_data', 'write'))
        
        # Bob作为data_editor应该可以读取和写入客户数据
        self.assertTrue(self.rbac.has_permission(1002, 'customer_data', 'read'))
        self.assertTrue(self.rbac.has_permission(1002, 'customer_data', 'write'))
        
        logger.info("直接权限分配测试通过")
    
    def test_permission_inheritance(self):
        """测试权限继承"""
        logger.info("开始测试权限继承")
        
        # Data_editor应该继承analyst的所有权限
        self.assertTrue(self.rbac.has_permission(1002, 'financial_data', 'read'))
        
        # Admin应该继承所有权限
        self.assertTrue(self.rbac.has_permission(1003, 'customer_data', 'read'))
        self.assertTrue(self.rbac.has_permission(1003, 'customer_data', 'write'))
        self.assertTrue(self.rbac.has_permission(1003, 'financial_data', 'read'))
        
        logger.info("权限继承测试通过")
    
    def test_role_revocation(self):
        """测试角色撤销"""
        logger.info("开始测试角色撤销")
        
        # 撤销Bob的data_editor角色
        self.rbac.revoke_role_from_user(1002, 102)
        
        # Bob现在应该没有任何权限
        self.assertFalse(self.rbac.has_permission(1002, 'customer_data', 'read'))
        self.assertFalse(self.rbac.has_permission(1002, 'customer_data', 'write'))
        
        logger.info("角色撤销测试通过")
    
    def test_permission_boundary(self):
        """测试权限边界"""
        logger.info("开始测试权限边界")
        
        # Alice不应该有写入财务数据的权限
        self.assertFalse(self.rbac.has_permission(1001, 'financial_data', 'write'))
        
        # Bob不应该有写入财务数据的权限
        self.assertFalse(self.rbac.has_permission(1002, 'financial_data', 'write'))
        
        # 只有Carol应该有访问admin_panel的权限
        self.assertFalse(self.rbac.has_permission(1001, 'admin_panel', 'access'))
        self.assertFalse(self.rbac.has_permission(1002, 'admin_panel', 'access'))
        self.assertTrue(self.rbac.has_permission(1003, 'admin_panel', 'access'))
        
        logger.info("权限边界测试通过")
    
    def test_minimum_privilege_principle(self):
        """测试最小权限原则"""
        logger.info("开始测试最小权限原则")
        
        # 获取每个用户的有效权限
        alice_permissions = self.rbac.get_user_effective_permissions(1001)
        bob_permissions = self.rbac.get_user_effective_permissions(1002)
        carol_permissions = self.rbac.get_user_effective_permissions(1003)
        
        # 验证权限递增性（高级角色拥有更多权限）
        self.assertTrue(len(alice_permissions) <= len(bob_permissions) <= len(carol_permissions))
        
        # 生成权限报告
        self._generate_privilege_report()
        
        logger.info("最小权限原则测试通过")
    
    def _generate_privilege_report(self):
        """生成权限审计报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'users': []
        }
        
        for user_id, user in self.rbac.users.items():
            user_report = {
                'user_id': user_id,
                'username': user.username,
                'roles': [role.role_name for role in user.roles],
                'permissions': [str(perm) for perm in self.rbac.get_user_effective_permissions(user_id)]
            }
            report['users'].append(user_report)
        
        # 保存报告到文件
        with open('rbac_privilege_audit_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("权限审计报告已生成: rbac_privilege_audit_report.json")

# 测试会话管理的额外测试用例
class SessionManagementTest(unittest.TestCase):
    """会话管理测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.sessions = {}
        self.session_timeout = timedelta(minutes=30)
    
    def create_session(self, user_id):
        """创建新会话"""
        import uuid
        session_id = str(uuid.uuid4())
        now = datetime.now()
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': now,
            'last_activity': now,
            'is_valid': True
        }
        return session_id
    
    def validate_session(self, session_id):
        """验证会话有效性"""
        if session_id not in self.sessions:
            return False, "会话不存在"
        
        session = self.sessions[session_id]
        
        # 检查会话是否被标记为无效
        if not session['is_valid']:
            return False, "会话已被终止"
        
        # 检查会话是否超时
        now = datetime.now()
        if now - session['last_activity'] > self.session_timeout:
            session['is_valid'] = False
            return False, "会话已超时"
        
        # 更新最后活动时间
        session['last_activity'] = now
        return True, "会话有效"
    
    def terminate_session(self, session_id):
        """终止会话"""
        if session_id in self.sessions:
            self.sessions[session_id]['is_valid'] = False
            return True
        return False
    
    def test_session_creation_and_validation(self):
        """测试会话创建和验证"""
        logger.info("开始测试会话创建和验证")
        
        # 创建会话
        session_id = self.create_session(1001)
        self.assertIn(session_id, self.sessions)
        
        # 验证有效会话
        is_valid, message = self.validate_session(session_id)
        self.assertTrue(is_valid)
        self.assertEqual(message, "会话有效")
        
        logger.info("会话创建和验证测试通过")
    
    def test_session_timeout(self):
        """测试会话超时"""
        logger.info("开始测试会话超时")
        
        # 创建会话
        session_id = self.create_session(1001)
        
        # 手动设置最后活动时间为超过超时时间
        self.sessions[session_id]['last_activity'] = datetime.now() - self.session_timeout - timedelta(minutes=1)
        
        # 验证会话应超时
        is_valid, message = self.validate_session(session_id)
        self.assertFalse(is_valid)
        self.assertEqual(message, "会话已超时")
        
        # 验证会话被标记为无效
        self.assertFalse(self.sessions[session_id]['is_valid'])
        
        logger.info("会话超时测试通过")
    
    def test_session_termination(self):
        """测试会话终止"""
        logger.info("开始测试会话终止")
        
        # 创建会话
        session_id = self.create_session(1001)
        
        # 终止会话
        self.assertTrue(self.terminate_session(session_id))
        
        # 验证终止后的会话
        is_valid, message = self.validate_session(session_id)
        self.assertFalse(is_valid)
        self.assertEqual(message, "会话已被终止")
        
        logger.info("会话终止测试通过")

def run_tests():
    """运行所有测试"""
    # 运行RBAC测试
    rbac_suite = unittest.TestLoader().loadTestsFromTestCase(RBACSecurityTester)
    rbac_result = unittest.TextTestRunner(verbosity=2).run(rbac_suite)
    
    # 运行会话管理测试
    session_suite = unittest.TestLoader().loadTestsFromTestCase(SessionManagementTest)
    session_result = unittest.TextTestRunner(verbosity=2).run(session_suite)
    
    # 返回测试结果摘要
    return {
        'rbac_tests': {
            'total': rbac_result.testsRun,
            'failures': len(rbac_result.failures),
            'errors': len(rbac_result.errors)
        },
        'session_tests': {
            'total': session_result.testsRun,
            'failures': len(session_result.failures),
            'errors': len(session_result.errors)
        }
    }

if __name__ == "__main__":
    # 运行测试并生成报告
    test_results = run_tests()
    
    # 输出测试结果摘要
    print(f"\n测试结果摘要:")
    print(f"RBAC测试 - 总测试数: {test_results['rbac_tests']['total']}, 失败: {test_results['rbac_tests']['failures']}, 错误: {test_results['rbac_tests']['errors']}")
    print(f"会话管理测试 - 总测试数: {test_results['session_tests']['total']}, 失败: {test_results['session_tests']['failures']}, 错误: {test_results['session_tests']['errors']}")
    
    # 如果所有测试通过
    if test_results['rbac_tests']['failures'] == 0 and test_results['rbac_tests']['errors'] == 0 and \
       test_results['session_tests']['failures'] == 0 and test_results['session_tests']['errors'] == 0:
        print("\n所有安全测试通过!")
    else:
        print("\n安全测试存在失败，请检查问题并修复。")
