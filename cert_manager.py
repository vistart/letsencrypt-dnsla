#!/usr/bin/env python3
"""
证书管理器
整合DNS.LA和ACME客户端，实现自动化证书管理
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend

from acme_client import ACMEClient
from dnsla_client import DNSLAClient


logger = logging.getLogger(__name__)


class CertificateManager:
    """证书管理器"""
    
    def __init__(
        self,
        dnsla_client: DNSLAClient,
        acme_client: ACMEClient,
        domain_id: str,
        propagation_seconds: int = 120
    ):
        """
        初始化证书管理器
        
        Args:
            dnsla_client: DNS.LA客户端
            acme_client: ACME客户端
            domain_id: DNS.LA域名ID
            propagation_seconds: DNS记录生效等待时间（秒）
        """
        self.dns = dnsla_client
        self.acme = acme_client
        self.domain_id = domain_id
        self.propagation_seconds = propagation_seconds
        
        logger.info("证书管理器初始化成功")
    
    def _extract_host_from_validation_name(self, validation_name: str, base_domain: str) -> str:
        """
        从验证域名提取主机头
        
        例如: _acme-challenge.example.com -> _acme-challenge
              _acme-challenge.www.example.com -> _acme-challenge.www
        
        Args:
            validation_name: 验证域名（如_acme-challenge.example.com）
            base_domain: 基础域名（如example.com）
            
        Returns:
            主机头
        """
        # 移除基础域名部分
        if validation_name.endswith('.' + base_domain):
            host = validation_name[:-len(base_domain)-1]
        elif validation_name == base_domain:
            host = '@'
        else:
            host = validation_name
        
        return host
    
    def issue_certificate(
        self,
        domains: List[str],
        cert_dir: str = "./certs",
        key_size: int = 2048
    ) -> Optional[Path]:
        """
        颁发证书
        
        Args:
            domains: 域名列表（第一个为主域名）
            cert_dir: 证书存储目录
            key_size: RSA密钥大小
            
        Returns:
            证书目录路径，失败返回None
        """
        logger.info("=" * 60)
        logger.info("开始颁发证书")
        logger.info(f"域名: {', '.join(domains)}")
        logger.info("=" * 60)
        
        # 1. 生成证书和创建订单
        logger.info("\n[步骤 1/5] 生成证书私钥和创建ACME订单...")
        result = self.acme.generate_certificate(domains, cert_dir, key_size)
        if not result:
            return None
        
        cert_path, order, private_key = result
        
        # 2. 获取DNS挑战
        logger.info("\n[步骤 2/5] 获取DNS-01挑战...")
        dns_challenges = []
        for authz in order.authorizations:
            for challenge in authz.body.challenges:
                from acme import challenges
                if isinstance(challenge.chall, challenges.DNS01):
                    dns_challenges.append(challenge)
        
        if not dns_challenges:
            logger.error("未找到DNS-01挑战")
            return None
        
        logger.info(f"获取到 {len(dns_challenges)} 个DNS-01挑战")
        
        # 3. 设置DNS验证记录
        logger.info("\n[步骤 3/5] 设置DNS验证记录...")
        record_ids = []
        base_domain = domains[0].lstrip('*.')  # 移除通配符前缀
        
        for challenge in dns_challenges:
            domain, validation_name, validation_value = self.acme.get_dns_challenge_data(challenge)
            
            # 提取主机头
            host = self._extract_host_from_validation_name(validation_name, base_domain)
            
            logger.info(f"  域名: {domain}")
            logger.info(f"  验证记录: {host} -> {validation_value}")
            
            # 删除旧的验证记录（如果存在）
            self.dns.delete_txt_records(self.domain_id, host)
            
            # 添加新的验证记录
            record_id = self.dns.add_txt_record(
                domain_id=self.domain_id,
                host=host,
                value=validation_value,
                ttl=600  # 10分钟TTL
            )
            
            if record_id:
                record_ids.append((record_id, host))
            else:
                logger.error(f"添加DNS记录失败: {host}")
                # 清理已添加的记录
                for rid, _ in record_ids:
                    self.dns.delete_record(rid)
                return None
        
        # 4. 等待DNS记录生效
        logger.info(f"\n[步骤 4/5] 等待DNS记录生效（{self.propagation_seconds}秒）...")
        self.dns.wait_for_propagation(self.propagation_seconds)
        
        # 5. 回答挑战并等待验证
        logger.info("\n[步骤 5/5] 提交挑战响应并等待Let's Encrypt验证...")
        for challenge in dns_challenges:
            if not self.acme.answer_challenge(challenge):
                logger.error("提交挑战响应失败")
                # 清理DNS记录
                for record_id, _ in record_ids:
                    self.dns.delete_record(record_id)
                return None
        
        # 轮询订单状态
        completed_order = self.acme.poll_order(order)
        
        # 6. 清理DNS验证记录
        logger.info("\n清理DNS验证记录...")
        for record_id, host in record_ids:
            self.dns.delete_record(record_id)
            logger.info(f"  已删除: {host}")
        
        # 7. 保存证书
        if completed_order and completed_order.fullchain_pem:
            logger.info("\n保存证书文件...")
            if self.acme.save_certificate(completed_order, cert_path, domains):
                logger.info("\n" + "=" * 60)
                logger.info("证书颁发成功！")
                logger.info(f"证书路径: {cert_path}")
                logger.info("=" * 60)
                return cert_path
        
        logger.error("\n证书颁发失败")
        return None
    
    def get_certificate_info(self, cert_file: str) -> Optional[Dict]:
        """
        获取证书信息
        
        Args:
            cert_file: 证书文件路径
            
        Returns:
            证书信息字典
        """
        cert_path = Path(cert_file)
        if not cert_path.exists():
            logger.error(f"证书文件不存在: {cert_file}")
            return None
        
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # 提取信息
            info = {
                'subject': cert.subject.rfc4514_string(),
                'issuer': cert.issuer.rfc4514_string(),
                'serial_number': cert.serial_number,
                'not_valid_before': cert.not_valid_before_utc,
                'not_valid_after': cert.not_valid_after_utc,
                'version': cert.version.name,
                'signature_algorithm': cert.signature_algorithm_oid._name,
                'domains': [],
            }
            
            # 提取SAN（Subject Alternative Names）
            try:
                san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                info['domains'] = [name.value for name in san_ext.value]
            except x509.ExtensionNotFound:
                pass
            
            # 计算剩余天数
            now = datetime.utcnow()
            days_remaining = (cert.not_valid_after_utc.replace(tzinfo=None) - now).days
            info['days_remaining'] = days_remaining
            
            return info
            
        except Exception as e:
            logger.error(f"读取证书信息失败: {e}")
            return None
    
    def check_certificate_expiry(
        self,
        cert_file: str,
        renew_days: int = 30
    ) -> bool:
        """
        检查证书是否需要续期
        
        Args:
            cert_file: 证书文件路径
            renew_days: 提前续期天数
            
        Returns:
            True表示需要续期，False表示不需要
        """
        info = self.get_certificate_info(cert_file)
        if not info:
            return True  # 证书不存在或无效，需要颁发新证书
        
        days_remaining = info['days_remaining']
        logger.info(f"证书剩余天数: {days_remaining}")
        
        if days_remaining <= renew_days:
            logger.info(f"证书将在 {days_remaining} 天后过期，需要续期")
            return True
        else:
            logger.info(f"证书还有 {days_remaining} 天过期，暂不需要续期")
            return False
    
    def renew_certificate(
        self,
        domains: List[str],
        cert_dir: str = "./certs",
        key_size: int = 2048,
        renew_days: int = 30
    ) -> Optional[Path]:
        """
        续期证书
        
        Args:
            domains: 域名列表
            cert_dir: 证书存储目录
            key_size: RSA密钥大小
            renew_days: 提前续期天数
            
        Returns:
            证书目录路径，失败返回None
        """
        cert_file = Path(cert_dir) / domains[0] / "cert.pem"
        
        # 检查是否需要续期
        if not self.check_certificate_expiry(str(cert_file), renew_days):
            logger.info("证书无需续期")
            return Path(cert_dir) / domains[0]
        
        # 颁发新证书
        logger.info("开始续期证书...")
        return self.issue_certificate(domains, cert_dir, key_size)
    
    def revoke_certificate(self, cert_file: str, reason: int = 0) -> bool:
        """
        吊销证书
        
        Args:
            cert_file: 证书文件路径
            reason: 吊销原因代码
                0 - unspecified
                1 - keyCompromise
                3 - affiliationChanged
                4 - superseded
                5 - cessationOfOperation
            
        Returns:
            是否成功
        """
        cert_path = Path(cert_file)
        if not cert_path.exists():
            logger.error(f"证书文件不存在: {cert_file}")
            return False
        
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            # 吊销证书
            from acme import messages
            self.acme.acme_client.revoke(
                messages.Revocation(certificate=cert),
                reason=reason
            )
            
            logger.info(f"证书已吊销: {cert_file}")
            return True
            
        except Exception as e:
            logger.error(f"吊销证书失败: {e}")
            return False
    
    def list_certificates(self, cert_dir: str = "./certs") -> List[Dict]:
        """
        列出所有证书
        
        Args:
            cert_dir: 证书存储目录
            
        Returns:
            证书信息列表
        """
        cert_path = Path(cert_dir)
        if not cert_path.exists():
            logger.warning(f"证书目录不存在: {cert_dir}")
            return []
        
        certificates = []
        
        for domain_dir in cert_path.iterdir():
            if domain_dir.is_dir():
                cert_file = domain_dir / "cert.pem"
                if cert_file.exists():
                    info = self.get_certificate_info(str(cert_file))
                    if info:
                        info['domain'] = domain_dir.name
                        info['cert_path'] = str(domain_dir)
                        certificates.append(info)
        
        return certificates
    
    def display_certificate_info(self, cert_file: str):
        """
        显示证书信息（格式化输出）
        
        Args:
            cert_file: 证书文件路径
        """
        info = self.get_certificate_info(cert_file)
        if not info:
            return
        
        print("\n" + "=" * 70)
        print("证书信息")
        print("=" * 70)
        print(f"主题: {info['subject']}")
        print(f"颁发者: {info['issuer']}")
        print(f"序列号: {info['serial_number']}")
        print(f"版本: {info['version']}")
        print(f"签名算法: {info['signature_algorithm']}")
        print(f"生效时间: {info['not_valid_before']}")
        print(f"过期时间: {info['not_valid_after']}")
        print(f"剩余天数: {info['days_remaining']} 天")
        print(f"\n域名列表:")
        for domain in info['domains']:
            print(f"  - {domain}")
        print("=" * 70)


if __name__ == '__main__':
    # 测试代码
    import yaml
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
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
    
    # 创建证书管理器
    manager = CertificateManager(
        dnsla_client=dns_client,
        acme_client=acme_client,
        domain_id=config['domains'][0]['domain_id'],
        propagation_seconds=config['dnsla']['propagation_seconds']
    )
    
    print("证书管理器创建成功")
