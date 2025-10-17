# !/usr/bin/env python3
"""
Let's Encrypt 证书管理工具
使用DNS.LA API进行DNS-01验证
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

from acme_client import ACMEClient
from cert_manager import CertificateManager
from dnsla_client import DNSLAClient


# 配置日志
def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('letsencrypt.log', encoding='utf-8')
        ]
    )


def load_config(config_file: str = 'config.yaml') -> dict:
    """加载配置文件"""
    config_path = Path(config_file)
    if not config_path.exists():
        print(f"错误: 配置文件不存在: {config_file}")
        print("请先复制config.yaml.example为config.yaml并修改配置")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_manager(config: dict) -> CertificateManager:
    """创建证书管理器"""
    # 创建DNS客户端
    dns_client = DNSLAClient(
        api_id=config['dnsla']['api_id'],
        api_secret=config['dnsla']['api_secret'],
        base_url=config['dnsla']['base_url']
    )

    # 创建ACME客户端
    acme_client = ACMEClient(
        email=config['letsencrypt']['email'],
        account_dir=config['letsencrypt']['account_dir'],
        staging=config['letsencrypt']['staging']
    )

    # 创建证书管理器
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        base_domain=config['domains'][0]['domain'],
        domain_id=config['domains'][0]['domain_id'],
        propagation_seconds=config['dnsla']['propagation_seconds']
    )

    return manager


def cmd_issue(args, config):
    """颁发证书命令"""
    manager = create_manager(config)

    # 获取域名列表
    if args.domains:
        domains = args.domains
    else:
        # 从配置文件读取
        base_domain = config['domains'][0]['domain']
        subdomains = config['domains'][0].get('subdomains', ['@'])

        domains = []
        for subdomain in subdomains:
            if subdomain == '@':
                domains.append(base_domain)
            elif subdomain.startswith('*.'):
                # 通配符域名
                domains.append(subdomain)
            else:
                domains.append(f"{subdomain}.{base_domain}")

    print(f"\n准备为以下域名颁发证书:")
    for domain in domains:
        print(f"  - {domain}")
    print()

    # 颁发证书
    cert_path = manager.issue_certificate(
        domains=domains,
        cert_dir=config['letsencrypt']['cert_dir'],
        key_size=config['certificate']['key_size']
    )

    if cert_path:
        print(f"\n✓ 证书颁发成功！")
        print(f"证书路径: {cert_path}")

        # 显示证书信息
        cert_file = cert_path / "cert.pem"
        manager.display_certificate_info(str(cert_file))
    else:
        print("\n✗ 证书颁发失败")
        sys.exit(1)


def cmd_renew(args, config):
    """续期证书命令"""
    manager = create_manager(config)

    # 获取域名列表
    if args.domains:
        domains = args.domains
    else:
        base_domain = config['domains'][0]['domain']
        subdomains = config['domains'][0].get('subdomains', ['@'])

        domains = []
        for subdomain in subdomains:
            if subdomain == '@':
                domains.append(base_domain)
            elif subdomain.startswith('*.'):
                domains.append(subdomain)
            else:
                domains.append(f"{subdomain}.{base_domain}")

    # 续期证书
    cert_path = manager.renew_certificate(
        domains=domains,
        cert_dir=config['letsencrypt']['cert_dir'],
        key_size=config['certificate']['key_size'],
        renew_days=config['certificate']['renew_days']
    )

    if cert_path:
        print(f"\n✓ 证书续期成功！")
        print(f"证书路径: {cert_path}")
    else:
        print("\n✗ 证书续期失败")
        sys.exit(1)


def cmd_info(args, config):
    """查看证书信息命令"""
    manager = create_manager(config)

    if args.cert_file:
        # 查看指定证书
        manager.display_certificate_info(args.cert_file)
    else:
        # 查看域名证书
        domain = args.domain or config['domains'][0]['domain']
        cert_file = Path(config['letsencrypt']['cert_dir']) / domain / "cert.pem"

        if not cert_file.exists():
            print(f"错误: 证书不存在: {cert_file}")
            sys.exit(1)

        manager.display_certificate_info(str(cert_file))


def cmd_list(args, config):
    """列出所有证书命令"""
    manager = create_manager(config)

    certificates = manager.list_certificates(config['letsencrypt']['cert_dir'])

    if not certificates:
        print("没有找到任何证书")
        return

    print(f"\n找到 {len(certificates)} 个证书:")
    print("\n" + "=" * 80)

    for cert in certificates:
        status = "✓ 有效" if cert['days_remaining'] > 30 else "⚠ 即将过期"
        if cert['days_remaining'] < 0:
            status = "✗ 已过期"

        print(f"域名: {cert['domain']}")
        print(f"路径: {cert['cert_path']}")
        print(f"过期时间: {cert['not_valid_after']}")
        print(f"剩余天数: {cert['days_remaining']} 天")
        print(f"状态: {status}")
        print(f"域名列表: {', '.join(cert['domains'])}")
        print("-" * 80)


def cmd_revoke(args, config):
    """吊销证书命令"""
    manager = create_manager(config)

    if args.cert_file:
        cert_file = args.cert_file
    else:
        domain = args.domain or config['domains'][0]['domain']
        cert_file = Path(config['letsencrypt']['cert_dir']) / domain / "cert.pem"
        cert_file = str(cert_file)

    if not Path(cert_file).exists():
        print(f"错误: 证书不存在: {cert_file}")
        sys.exit(1)

    # 确认吊销
    print(f"\n警告: 即将吊销证书: {cert_file}")
    confirm = input("确认吊销? (yes/no): ")
    if confirm.lower() != 'yes':
        print("已取消")
        return

    # 吊销证书
    if manager.revoke_certificate(cert_file, reason=args.reason):
        print("\n✓ 证书已吊销")
    else:
        print("\n✗ 证书吊销失败")
        sys.exit(1)


def cmd_test_dns(args, config):
    """测试DNS API命令"""
    dns_client = DNSLAClient(
        api_id=config['dnsla']['api_id'],
        api_secret=config['dnsla']['api_secret'],
        base_url=config['dnsla']['base_url']
    )

    domain = config['domains'][0]['domain']
    domain_id = config['domains'][0]['domain_id']

    print(f"\n测试DNS.LA API...")
    print(f"域名: {domain}")
    print(f"域名ID: {domain_id}")

    # 测试获取域名信息
    print("\n1. 测试获取域名信息...")
    domain_info = dns_client.get_domain_info(domain)
    if domain_info:
        print(f"  ✓ 成功: {domain_info['displayDomain']}")
    else:
        print("  ✗ 失败")
        return

    # 测试获取记录列表
    print("\n2. 测试获取DNS记录...")
    records = dns_client.get_record_list(domain_id)
    print(f"  ✓ 成功: 找到 {len(records)} 条记录")

    # 测试添加TXT记录
    print("\n3. 测试添加TXT记录...")
    test_host = "_acme-challenge-test"
    test_value = "test-validation-value"
    record_id = dns_client.add_txt_record(domain_id, test_host, test_value)
    if record_id:
        print(f"  ✓ 成功: 记录ID {record_id}")

        # 测试删除记录
        print("\n4. 测试删除TXT记录...")
        if dns_client.delete_record(record_id):
            print("  ✓ 成功")
        else:
            print("  ✗ 失败")
    else:
        print("  ✗ 失败")

    print("\nDNS API测试完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Let\'s Encrypt证书管理工具（使用DNS.LA API）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 颁发证书
  %(prog)s issue
  %(prog)s issue -d example.com -d www.example.com

  # 续期证书
  %(prog)s renew

  # 查看证书信息
  %(prog)s info
  %(prog)s info -d example.com

  # 列出所有证书
  %(prog)s list

  # 吊销证书
  %(prog)s revoke -d example.com

  # 测试DNS API
  %(prog)s test-dns
        """
    )

    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # issue命令
    parser_issue = subparsers.add_parser('issue', help='颁发新证书')
    parser_issue.add_argument(
        '-d', '--domains',
        nargs='+',
        help='域名列表（不指定则使用配置文件）'
    )

    # renew命令
    parser_renew = subparsers.add_parser('renew', help='续期证书')
    parser_renew.add_argument(
        '-d', '--domains',
        nargs='+',
        help='域名列表（不指定则使用配置文件）'
    )

    # info命令
    parser_info = subparsers.add_parser('info', help='查看证书信息')
    parser_info.add_argument(
        '-d', '--domain',
        help='域名'
    )
    parser_info.add_argument(
        '-f', '--cert-file',
        help='证书文件路径'
    )

    # list命令
    parser_list = subparsers.add_parser('list', help='列出所有证书')

    # revoke命令
    parser_revoke = subparsers.add_parser('revoke', help='吊销证书')
    parser_revoke.add_argument(
        '-d', '--domain',
        help='域名'
    )
    parser_revoke.add_argument(
        '-f', '--cert-file',
        help='证书文件路径'
    )
    parser_revoke.add_argument(
        '-r', '--reason',
        type=int,
        default=0,
        choices=[0, 1, 3, 4, 5],
        help='吊销原因 (0=unspecified, 1=keyCompromise, 3=affiliationChanged, 4=superseded, 5=cessationOfOperation)'
    )

    # test-dns命令
    parser_test = subparsers.add_parser('test-dns', help='测试DNS API')

    args = parser.parse_args()

    # 设置日志
    setup_logging(args.verbose)

    # 加载配置
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"错误: 加载配置文件失败: {e}")
        sys.exit(1)

    # 执行命令
    if args.command == 'issue':
        cmd_issue(args, config)
    elif args.command == 'renew':
        cmd_renew(args, config)
    elif args.command == 'info':
        cmd_info(args, config)
    elif args.command == 'list':
        cmd_list(args, config)
    elif args.command == 'revoke':
        cmd_revoke(args, config)
    elif args.command == 'test-dns':
        cmd_test_dns(args, config)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()