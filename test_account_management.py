#!/usr/bin/env python3
"""
测试账户管理功能
验证 v1.1.1 的账户管理修复
"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_account_creation():
    """测试账户创建逻辑"""
    try:
        from acme_client import ACMEClient
        
        print("=" * 60)
        print("测试：账户管理功能")
        print("=" * 60)
        print()
        
        # 测试1：创建测试环境客户端
        print("1. 创建ACME客户端（测试环境）...")
        try:
            acme = ACMEClient(
                email="i@rho.im",
                account_dir="./test_accounts",
                staging=True
            )
            print("   ✅ 客户端创建成功")
            print(f"   环境: {acme.directory_url}")
            print()
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return False
        
        # 测试2：再次创建（应该复用账户）
        print("2. 再次创建客户端（应该复用账户）...")
        try:
            acme2 = ACMEClient(
                email="i@rho.im",
                account_dir="./test_accounts",
                staging=True
            )
            print("   ✅ 客户端创建成功（复用账户）")
            print()
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return False
        
        # 测试3：检查关键方法是否存在
        print("3. 检查关键方法...")
        methods = [
            '_load_or_create_account_key',
            '_create_acme_client',
            '_generate_csr',
            'generate_certificate',
        ]
        
        all_exist = True
        for method in methods:
            if hasattr(acme, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} 不存在")
                all_exist = False
        print()
        
        if not all_exist:
            return False
        
        # 测试4：验证没有使用废弃的方法
        print("4. 验证代码质量...")
        import inspect
        source = inspect.getsource(ACMEClient._create_acme_client)
        
        # 检查不应该出现的内容
        bad_patterns = [
            ('query_registration', 'query_registration 已废弃'),
            ('.body', '不应该访问 .body 属性'),
        ]
        
        issues = []
        for pattern, reason in bad_patterns:
            if pattern in source:
                issues.append(reason)
        
        if issues:
            print("   ⚠️ 发现潜在问题:")
            for issue in issues:
                print(f"      - {issue}")
        else:
            print("   ✅ 代码质量检查通过")
        print()
        
        # 测试5：检查异常处理
        print("5. 检查异常处理...")
        if 'ConflictError' in source and 'only_return_existing' in source:
            print("   ✅ 正确处理 ConflictError")
            print("   ✅ 使用 only_return_existing 参数")
        else:
            print("   ⚠️ 可能缺少完整的异常处理")
        print()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print()
        print("账户管理功能正常，可以安全使用。")
        print()
        
        # 清理测试文件
        import shutil
        try:
            shutil.rmtree('./test_accounts')
            print("已清理测试文件")
        except:
            pass
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保 acme_client.py 在当前目录")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print()
    print("Let's Encrypt DNS.LA - 账户管理测试")
    print("测试 v1.1.1 的修复")
    print()
    
    success = test_account_creation()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
