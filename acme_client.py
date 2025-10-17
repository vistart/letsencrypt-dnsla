#!/usr/bin/env python3
"""
ACME客户端
使用certbot库与Let's Encrypt交互
"""

import logging
import os
import time
from pathlib import Path
from typing import List, Optional, Tuple

from acme import challenges, client, crypto_util as acme_crypto, messages
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509.oid import NameOID
import josepy as jose

logger = logging.getLogger(__name__)


class ACMEClient:
    """ACME客户端,用于与Let's Encrypt交互"""

    # Let's Encrypt服务器URL
    PRODUCTION_URL = 'https://acme-v02.api.letsencrypt.org/directory'
    STAGING_URL = 'https://acme-staging-v02.api.letsencrypt.org/directory'

    def __init__(
            self,
            email: str,
            account_dir: str = "./accounts",
            staging: bool = False
    ):
        """
        初始化ACME客户端

        Args:
            email: 联系邮箱
            account_dir: 账户密钥存储目录
            staging: 是否使用测试环境
        """
        self.email = email
        self.account_dir = Path(account_dir)
        self.account_dir.mkdir(parents=True, exist_ok=True)

        self.staging = staging
        self.directory_url = self.STAGING_URL if staging else self.PRODUCTION_URL

        # 初始化账户
        self.account_key = self._load_or_create_account_key()
        self.acme_client = self._create_acme_client()

        env = "测试" if staging else "生产"
        logger.info(f"ACME客户端初始化成功({env}环境)")

    def _load_or_create_account_key(self) -> jose.JWKRSA:
        """
        加载或创建账户密钥

        Returns:
            JOSE格式的账户密钥
        """
        key_file = self.account_dir / "account.key"

        if key_file.exists():
            logger.info("加载已有账户密钥")
            with open(key_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
        else:
            logger.info("创建新的账户密钥")
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            # 保存密钥
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open(key_file, 'wb') as f:
                f.write(pem)

            os.chmod(key_file, 0o600)

        return jose.JWKRSA(key=private_key)

    def _create_acme_client(self) -> client.ClientV2:
        """
        创建ACME客户端(智能账户管理)

        Returns:
            ACME客户端实例
        """
        from acme import errors

        net = client.ClientNetwork(self.account_key, user_agent='letsencrypt-dnsla/1.0')
        directory = messages.Directory.from_json(net.get(self.directory_url).json())
        acme_client = client.ClientV2(directory, net=net)

        # 智能账户管理
        try:
            logger.info(f"尝试注册或获取账户: {self.email}")

            # 创建注册请求
            new_reg = messages.NewRegistration.from_data(
                email=self.email,
                terms_of_service_agreed=True
            )

            try:
                # 尝试注册新账户
                regr = acme_client.new_account(new_reg)
                logger.info(f"新账户注册成功: {self.email}")

            except errors.ConflictError as conflict:
                # 账户已存在 - 这是正常情况
                logger.info(f"账户已存在,获取现有账户: {self.email}")
                logger.debug(f"账户URI: {conflict.location}")

                # 使用only_return_existing参数重新请求
                existing_reg = messages.NewRegistration.from_data(
                    email=self.email,
                    terms_of_service_agreed=True,
                    only_return_existing=True
                )

                # 发送POST请求到newAccount端点
                response = acme_client._post(acme_client.directory['newAccount'], existing_reg)

                # 从响应创建注册资源
                regr = acme_client._regr_from_response(response)

                # 设置账户
                net.account = regr

                logger.info(f"成功获取已有账户信息")

        except Exception as e:
            logger.error(f"账户管理失败: {e}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(traceback.format_exc())
            raise

        # 验证账户已设置
        if net.account is None:
            raise Exception("账户未能正确设置,无法继续")

        logger.info(f"账户已成功设置,URI: {net.account.uri}")

        return acme_client

    def create_order(self, domains: List[str]) -> Tuple[messages.OrderResource, List[challenges.DNS01]]:
        """
        创建证书订单并获取DNS-01挑战

        Args:
            domains: 域名列表

        Returns:
            订单资源和DNS-01挑战列表
        """
        logger.info(f"为域名创建订单: {', '.join(domains)}")

        # 创建订单
        order = self.acme_client.new_order(
            [acme_crypto.make_csr(domain.encode(), [domain.encode()]) for domain in domains]
        )

        # 提取DNS-01挑战
        dns_challenges = []
        for authz in order.authorizations:
            for challenge in authz.body.challenges:
                if isinstance(challenge.chall, challenges.DNS01):
                    dns_challenges.append(challenge)

        logger.info(f"获取到 {len(dns_challenges)} 个DNS-01挑战")
        return order, dns_challenges

    def get_dns_challenge_data(self, challenge) -> Tuple[str, str, str]:
        """
        获取DNS挑战数据

        Args:
            challenge: DNS-01挑战

        Returns:
            (域名, 记录名, 记录值) 元组
        """
        domain = challenge.authz.body.identifier.value

        # 获取验证记录名
        validation_domain_name = challenge.chall.validation_domain_name(domain)

        # 获取验证记录值
        key_authorization = challenge.chall.key_authorization(self.account_key)
        validation = challenge.chall.validation(self.account_key)

        logger.debug(f"DNS挑战数据: {validation_domain_name} -> {validation}")

        return domain, validation_domain_name, validation

    def answer_challenge(self, challenge) -> bool:
        """
        回答挑战(告诉Let's Encrypt已经设置好DNS记录)

        Args:
            challenge: DNS-01挑战

        Returns:
            是否成功
        """
        try:
            response = challenge.response(self.account_key)
            self.acme_client.answer_challenge(challenge, response)
            logger.info("已向Let's Encrypt提交挑战响应")
            return True
        except Exception as e:
            logger.error(f"回答挑战失败: {e}")
            return False

    def poll_order(self, order: messages.OrderResource, max_attempts: int = 30) -> Optional[messages.OrderResource]:
        """
        轮询订单状态直到完成或失败

        Args:
            order: 订单资源
            max_attempts: 最大尝试次数

        Returns:
            完成的订单资源,失败返回None
        """
        logger.info("等待Let's Encrypt验证DNS记录...")

        for attempt in range(max_attempts):
            time.sleep(5)  # 每5秒检查一次

            try:
                order = self.acme_client.poll_and_finalize(order)

                if order.fullchain_pem:
                    logger.info("证书签发成功!")
                    return order

                logger.debug(f"订单状态: {order.body.status} (尝试 {attempt + 1}/{max_attempts})")

            except Exception as e:
                logger.error(f"轮询订单状态失败: {e}")
                continue

        logger.error("验证超时,证书签发失败")
        return None

    def _generate_csr(self, domains: List[str], private_key) -> bytes:
        """
        生成证书签名请求(CSR)

        Args:
            domains: 域名列表
            private_key: 私钥

        Returns:
            PEM格式的CSR
        """
        # 创建主题名称
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, domains[0]),
        ])

        # 创建SAN扩展(Subject Alternative Names)
        san_list = [x509.DNSName(domain) for domain in domains]

        # 构建CSR
        csr_builder = x509.CertificateSigningRequestBuilder()
        csr_builder = csr_builder.subject_name(subject)
        csr_builder = csr_builder.add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False
        )

        # 签名CSR
        csr = csr_builder.sign(private_key, hashes.SHA256(), default_backend())

        # 返回PEM格式
        return csr.public_bytes(serialization.Encoding.PEM)

    def generate_certificate(
            self,
            domains: List[str],
            cert_dir: str = "./certs",
            key_size: int = 2048
    ) -> Optional[Tuple[Path, messages.OrderResource, rsa.RSAPrivateKey]]:
        """
        生成证书(不包括DNS验证步骤)

        Args:
            domains: 域名列表
            cert_dir: 证书存储目录
            key_size: RSA密钥大小

        Returns:
            (证书目录路径, 订单, 私钥) 元组,失败返回None
        """
        cert_path = Path(cert_dir) / domains[0]
        cert_path.mkdir(parents=True, exist_ok=True)

        # 生成私钥
        logger.info("生成证书私钥...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )

        # 保存私钥
        key_file = cert_path / "privkey.pem"
        with open(key_file, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        os.chmod(key_file, 0o600)

        # 生成CSR
        logger.info("生成证书签名请求...")
        csr_pem = self._generate_csr(domains, private_key)

        # 创建订单
        order = self.acme_client.new_order(csr_pem)

        return cert_path, order, private_key

    def save_certificate(
            self,
            order: messages.OrderResource,
            cert_path: Path,
            domains: List[str]
    ) -> bool:
        """
        保存证书文件

        Args:
            order: 已完成的订单
            cert_path: 证书保存路径
            domains: 域名列表

        Returns:
            是否成功
        """
        try:
            # 保存完整证书链
            fullchain_file = cert_path / "fullchain.pem"
            with open(fullchain_file, 'w') as f:
                f.write(order.fullchain_pem)

            # 保存证书(不含中间证书)
            cert_file = cert_path / "cert.pem"
            with open(cert_file, 'w') as f:
                # fullchain包含服务器证书和中间证书,我们只取第一个
                certs = order.fullchain_pem.split('\n\n')
                f.write(certs[0] + '\n')

            # 保存中间证书链
            chain_file = cert_path / "chain.pem"
            with open(chain_file, 'w') as f:
                f.write('\n\n'.join(certs[1:]))

            logger.info(f"证书已保存到: {cert_path}")
            logger.info(f"  - 完整证书链: {fullchain_file}")
            logger.info(f"  - 服务器证书: {cert_file}")
            logger.info(f"  - 中间证书链: {chain_file}")
            logger.info(f"  - 私钥: {cert_path / 'privkey.pem'}")

            return True

        except Exception as e:
            logger.error(f"保存证书失败: {e}")
            return False


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建测试客户端
    acme = ACMEClient(
        email="i@rho.im",
        staging=True  # 使用测试环境
    )

    print("ACME客户端创建成功")
    print(f"Directory URL: {acme.directory_url}")