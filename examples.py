#!/usr/bin/env python3
"""
快速示例脚本
演示如何使用证书管理库
"""

import logging
from pathlib import Path

from acme_client import ACMEClient
from cert_manager import CertificateManager
from dnsla_client import DNSLAClient


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 1. 创建DNS.LA客户端
    dns_client = DNSLAClient(
        api_id="your_api_id",
        api_secret="your_api_secret"
    )
    
    # 2. 创建ACME客户端
    acme_client = ACMEClient(
        email="admin@example.com",
        staging=True  # 使用测试环境
    )
    
    # 3. 创建证书管理器
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id="your_domain_id",
        propagation_seconds=120
    )
    
    # 4. 颁发证书
    cert_path = manager.issue_certificate(
        domains=["example.com", "www.example.com"]
    )
    
    if cert_path:
        print(f"证书已保存到: {cert_path}")


def example_wildcard_certificate():
    """通配符证书示例"""
    print("\n" + "=" * 60)
    print("示例2: 颁发通配符证书")
    print("=" * 60)
    
    dns_client = DNSLAClient(
        api_id="your_api_id",
        api_secret="your_api_secret"
    )
    
    acme_client = ACMEClient(
        email="admin@example.com",
        staging=True
    )
    
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id="your_domain_id"
    )
    
    # 颁发通配符证书
    cert_path = manager.issue_certificate(
        domains=["example.com", "*.example.com"]
    )
    
    if cert_path:
        print(f"通配符证书已保存到: {cert_path}")


def example_certificate_info():
    """查看证书信息示例"""
    print("\n" + "=" * 60)
    print("示例3: 查看证书信息")
    print("=" * 60)
    
    dns_client = DNSLAClient(
        api_id="your_api_id",
        api_secret="your_api_secret"
    )
    
    acme_client = ACMEClient(
        email="admin@example.com",
        staging=True
    )
    
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id="your_domain_id"
    )
    
    # 获取证书信息
    cert_file = "./certs/example.com/cert.pem"
    info = manager.get_certificate_info(cert_file)
    
    if info:
        print(f"域名: {', '.join(info['domains'])}")
        print(f"过期时间: {info['not_valid_after']}")
        print(f"剩余天数: {info['days_remaining']} 天")


def example_certificate_renewal():
    """证书续期示例"""
    print("\n" + "=" * 60)
    print("示例4: 证书续期")
    print("=" * 60)
    
    dns_client = DNSLAClient(
        api_id="your_api_id",
        api_secret="your_api_secret"
    )
    
    acme_client = ACMEClient(
        email="admin@example.com",
        staging=True
    )
    
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id="your_domain_id"
    )
    
    # 续期证书（如果需要）
    cert_path = manager.renew_certificate(
        domains=["example.com"],
        renew_days=30  # 提前30天续期
    )
    
    if cert_path:
        print(f"证书已续期，保存到: {cert_path}")


def example_list_certificates():
    """列出所有证书示例"""
    print("\n" + "=" * 60)
    print("示例5: 列出所有证书")
    print("=" * 60)
    
    dns_client = DNSLAClient(
        api_id="your_api_id",
        api_secret="your_api_secret"
    )
    
    acme_client = ACMEClient(
        email="admin@example.com",
        staging=True
    )
    
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id="your_domain_id"
    )
    
    # 列出所有证书
    certificates = manager.list_certificates()
    
    print(f"找到 {len(certificates)} 个证书:")
    for cert in certificates:
        print(f"\n域名: {cert['domain']}")
        print(f"过期时间: {cert['not_valid_after']}")
        print(f"剩余天数: {cert['days_remaining']} 天")


def example_dns_operations():
    """DNS操作示例"""
    print("\n" + "=" * 60)
    print("示例6: DNS记录操作")
    print("=" * 60)
    
    dns_client = DNSLAClient(
        api_id="your_api_id",
        api_secret="your_api_secret"
    )
    
    domain_id = "your_domain_id"
    
    # 1. 获取域名信息
    domain_info = dns_client.get_domain_info("example.com")
    print(f"域名ID: {domain_info['id']}")
    
    # 2. 获取DNS记录列表
    records = dns_client.get_record_list(domain_id)
    print(f"DNS记录数: {len(records)}")
    
    # 3. 添加TXT记录
    record_id = dns_client.add_txt_record(
        domain_id=domain_id,
        host="_acme-challenge",
        value="test-validation-value",
        ttl=600
    )
    print(f"添加记录ID: {record_id}")
    
    # 4. 查找TXT记录
    txt_records = dns_client.find_txt_records(
        domain_id=domain_id,
        host="_acme-challenge"
    )
    print(f"找到 {len(txt_records)} 条TXT记录")
    
    # 5. 删除记录
    if record_id:
        dns_client.delete_record(record_id)
        print("记录已删除")


def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("示例7: 错误处理")
    print("=" * 60)
    
    try:
        dns_client = DNSLAClient(
            api_id="invalid_id",
            api_secret="invalid_secret"
        )
        
        # 尝试获取域名信息
        domain_info = dns_client.get_domain_info("example.com")
        
        if domain_info is None:
            print("错误: 无法获取域名信息")
            print("可能的原因:")
            print("  - API凭证错误")
            print("  - 域名不存在")
            print("  - 网络连接问题")
            
    except Exception as e:
        print(f"发生异常: {e}")


def example_config_from_yaml():
    """从YAML配置文件加载示例"""
    print("\n" + "=" * 60)
    print("示例8: 从配置文件加载")
    print("=" * 60)
    
    import yaml
    
    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 创建客户端
    dns_client = DNSLAClient(
        api_id=config['dnsla']['api_id'],
        api_secret=config['dnsla']['api_secret'],
        base_url=config['dnsla']['base_url']
    )
    
    acme_client = ACMEClient(
        email=config['letsencrypt']['email'],
        account_dir=config['letsencrypt']['account_dir'],
        staging=config['letsencrypt']['staging']
    )
    
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id=config['domains'][0]['domain_id'],
        propagation_seconds=config['dnsla']['propagation_seconds']
    )
    
    print("从配置文件加载成功")


if __name__ == '__main__':
    print("\nLet's Encrypt DNS.LA 证书管理工具 - 示例脚本")
    print("\n注意: 这些示例需要正确的API凭证才能运行")
    print("请修改示例中的 'your_api_id' 等占位符\n")
    
    # 取消注释你想运行的示例
    
    # example_basic_usage()
    # example_wildcard_certificate()
    # example_certificate_info()
    # example_certificate_renewal()
    # example_list_certificates()
    # example_dns_operations()
    # example_error_handling()
    # example_config_from_yaml()
    
    print("\n要运行示例，请取消注释相应的函数调用")
