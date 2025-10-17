# 快速参考

## 命令速查

### 安装配置

```bash
# 安装
./install.sh

# 或手动安装
pip install -r requirements.txt

# 激活虚拟环境（如果使用）
source venv/bin/activate
```

### 基础命令

```bash
# 测试DNS API
python main.py test-dns

# 颁发证书（使用配置文件）
python main.py issue

# 颁发证书（指定域名）
python main.py issue -d example.com -d www.example.com

# 颁发通配符证书
python main.py issue -d example.com -d "*.example.com"

# 查看证书信息
python main.py info
python main.py info -d example.com
python main.py info -f /path/to/cert.pem

# 列出所有证书
python main.py list

# 续期证书
python main.py renew
python main.py renew -d example.com

# 吊销证书
python main.py revoke -d example.com

# 查看帮助
python main.py --help
python main.py issue --help
```

## 配置文件模板

```yaml
letsencrypt:
  staging: true  # 首次使用设为true
  email: "your@email.com"
  cert_dir: "./certs"
  account_dir: "./accounts"

dnsla:
  base_url: "https://api.dns.la"
  api_id: "your_api_id"
  api_secret: "your_api_secret"
  propagation_seconds: 120

domains:
  - domain: "example.com"
    domain_id: "12345"
    subdomains:
      - "@"    # 根域名
      - "www"  # 子域名
      # - "*"  # 通配符

certificate:
  key_size: 2048
  renew_days: 30
```

## Web服务器配置

### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /path/to/certs/example.com/fullchain.pem;
    ssl_certificate_key /path/to/certs/example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### Apache

```apache
<VirtualHost *:443>
    ServerName example.com
    
    SSLEngine on
    SSLCertificateFile /path/to/certs/example.com/cert.pem
    SSLCertificateKeyFile /path/to/certs/example.com/privkey.pem
    SSLCertificateChainFile /path/to/certs/example.com/chain.pem
</VirtualHost>
```

## 数据库配置

### MySQL

```ini
[mysqld]
ssl-ca=/path/to/certs/example.com/chain.pem
ssl-cert=/path/to/certs/example.com/cert.pem
ssl-key=/path/to/certs/example.com/privkey.pem
require_secure_transport=ON
```

### PostgreSQL

```ini
ssl = on
ssl_ca_file = '/path/to/certs/example.com/chain.pem'
ssl_cert_file = '/path/to/certs/example.com/cert.pem'
ssl_key_file = '/path/to/certs/example.com/privkey.pem'
```

权限设置：
```bash
chown postgres:postgres /path/to/certs/example.com/privkey.pem
chmod 600 /path/to/certs/example.com/privkey.pem
```

### MongoDB

```yaml
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /path/to/combined.pem
    CAFile: /path/to/certs/example.com/chain.pem
```

合并证书：
```bash
cat fullchain.pem privkey.pem > combined.pem
chmod 600 combined.pem
chown mongodb:mongodb combined.pem
```

### Redis

```ini
tls-port 6380
port 0
tls-cert-file /path/to/certs/example.com/cert.pem
tls-key-file /path/to/certs/example.com/privkey.pem
tls-ca-cert-file /path/to/certs/example.com/chain.pem
```

## 自动续期设置

### Cron方式

```bash
# 创建续期脚本
cat > renew.sh << 'EOF'
#!/bin/bash
cd /path/to/letsencrypt-dnsla
source venv/bin/activate
python main.py renew
systemctl reload nginx
EOF

chmod +x renew.sh

# 添加到crontab
crontab -e
# 添加: 0 3 * * * /path/to/renew.sh >> /var/log/cert-renew.log 2>&1
```

### Systemd Timer方式

```bash
# 创建服务文件 /etc/systemd/system/cert-renew.service
[Unit]
Description=Renew Let's Encrypt Certificates
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/path/to/letsencrypt-dnsla
ExecStart=/path/to/letsencrypt-dnsla/venv/bin/python main.py renew

# 创建定时器 /etc/systemd/system/cert-renew.timer
[Unit]
Description=Daily certificate renewal

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target

# 启用
sudo systemctl daemon-reload
sudo systemctl enable cert-renew.timer
sudo systemctl start cert-renew.timer
```

## Python API示例

```python
from dnsla_client import DNSLAClient
from acme_client import ACMEClient
from cert_manager import CertificateManager

# 初始化客户端
dns = DNSLAClient(
    api_id="your_api_id",
    api_secret="your_api_secret"
)

acme = ACMEClient(
    email="admin@example.com",
    staging=True
)

# 创建管理器
manager = CertificateManager(
    dnsla_client=dns,
    acme_client=acme,
    domain_id="12345",
    propagation_seconds=120
)

# 颁发证书
cert_path = manager.issue_certificate(
    domains=["example.com", "www.example.com"]
)

# 查询证书信息
info = manager.get_certificate_info("./certs/example.com/cert.pem")
print(f"剩余 {info['days_remaining']} 天")

# 续期证书
manager.renew_certificate(
    domains=["example.com"],
    renew_days=30
)
```

## 获取DNS.LA凭证

```bash
# 1. 登录 https://www.dns.la
# 2. 进入"我的账户" -> "API密钥"
# 3. 获取 APIID 和 APISecret

# 获取域名ID
curl 'https://api.dns.la/api/domain?domain=example.com' \
  -H 'Authorization: Basic <token>'
```

## 计算Basic Auth Token

```python
import base64

api_id = "your_api_id"
api_secret = "your_api_secret"

credentials = f"{api_id}:{api_secret}"
token = base64.b64encode(credentials.encode()).decode()
print(f"Authorization: Basic {token}")
```

## 证书文件说明

```
certs/example.com/
├── cert.pem         # 服务器证书
├── chain.pem        # 中间证书链
├── fullchain.pem    # 完整证书链（推荐用于Nginx）
└── privkey.pem      # 私钥（权限600）
```

## 常用DNS记录类型

| 类型 | 值 | 说明 |
|------|---|------|
| A | 1 | IPv4地址 |
| NS | 2 | 名称服务器 |
| CNAME | 5 | 别名 |
| MX | 15 | 邮件服务器 |
| TXT | 16 | 文本记录（ACME验证用） |
| AAAA | 28 | IPv6地址 |
| SRV | 33 | 服务记录 |
| CAA | 257 | 证书颁发机构授权 |

## 吊销原因代码

| 代码 | 说明 |
|------|------|
| 0 | unspecified（未指定） |
| 1 | keyCompromise（密钥泄露） |
| 3 | affiliationChanged（归属变更） |
| 4 | superseded（已替换） |
| 5 | cessationOfOperation（停止运营） |

## 速率限制

- 每周每域名：50个证书
- 每个证书：最多100个域名
- 失败验证：每小时5次

详见：https://letsencrypt.org/docs/rate-limits/

## 故障排查

```bash
# 查看日志
tail -f letsencrypt.log

# 测试DNS API
python main.py test-dns

# 验证DNS记录
dig _acme-challenge.example.com TXT

# 检查证书
openssl x509 -in certs/example.com/cert.pem -text -noout

# 测试HTTPS
curl -vI https://example.com

# 测试数据库SSL
mysql --ssl-mode=REQUIRED --ssl-ca=chain.pem -h example.com -u user -p
```

## 文件权限

```bash
# 私钥权限
chmod 600 certs/*/privkey.pem

# 配置文件权限
chmod 600 config.yaml

# 证书目录权限
chmod 755 certs/
```

## 有用的链接

- Let's Encrypt: https://letsencrypt.org
- DNS.LA: https://www.dns.la
- Certbot文档: https://eff-certbot.readthedocs.io
- ACME规范: https://tools.ietf.org/html/rfc8555

## 项目文件

- README.md - 完整文档
- PROJECT_OVERVIEW.md - 项目概览
- examples.py - 代码示例
- QUICK_REFERENCE.md - 本文档
