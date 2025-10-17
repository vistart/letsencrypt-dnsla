# Let's Encrypt 证书管理工具（DNS.LA版本）

自动化Let's Encrypt证书颁发工具，使用DNS.LA API进行DNS-01验证。

## 特性

- ✅ 自动DNS-01验证（无需手动配置Web服务器）
- ✅ 支持单域名、多域名、通配符域名证书
- ✅ 自动DNS记录管理
- ✅ 证书查询、续期、吊销
- ✅ 详细的日志记录
- ✅ 测试环境支持（避免触发速率限制）
- ✅ Python库实现，易于扩展

## 系统要求

- Python 3.7+
- pip
- 域名托管在DNS.LA

## 安装

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd letsencrypt-dnsla
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或使用虚拟环境（推荐）：

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. 配置

编辑 `config.yaml` 文件：

```yaml
# Let's Encrypt 配置
letsencrypt:
  # 首次使用建议设为true，测试成功后改为false
  staging: true
  email: "your-email@example.com"
  cert_dir: "./certs"
  account_dir: "./accounts"

# DNS.LA API 配置
dnsla:
  base_url: "https://api.dns.la"
  api_id: "your_api_id"
  api_secret: "your_api_secret"
  # DNS记录生效等待时间（秒）
  propagation_seconds: 120

# 域名配置
domains:
  - domain: "example.com"
    domain_id: "your_domain_id"
    subdomains:
      - "@"  # 根域名
      - "www"
      # - "*.example.com"  # 通配符

certificate:
  key_size: 2048
  renew_days: 30
```

#### 获取DNS.LA API凭证

1. 登录 [DNS.LA](https://www.dns.la)
2. 进入"我的账户" -> "API密钥"
3. 获取 `APIID`（api_id）和 `APISecret`（api_secret）

#### 获取域名ID

方法一：使用测试命令
```bash
python main.py test-dns
```

方法二：手动查询
```bash
curl --location 'https://api.dns.la/api/domain?domain=example.com' \
--header 'Authorization: Basic <your_base64_token>'
```

## 使用方法

### 测试DNS API

首次使用前，建议测试DNS API连接：

```bash
python main.py test-dns
```

### 颁发证书

#### 使用配置文件中的域名

```bash
python main.py issue
```

#### 指定域名

```bash
# 单域名
python main.py issue -d example.com

# 多域名
python main.py issue -d example.com -d www.example.com

# 通配符域名
python main.py issue -d example.com -d "*.example.com"
```

### 查看证书信息

```bash
# 查看配置文件中的域名证书
python main.py info

# 查看指定域名证书
python main.py info -d example.com

# 查看指定证书文件
python main.py info -f ./certs/example.com/cert.pem
```

### 列出所有证书

```bash
python main.py list
```

### 续期证书

```bash
# 续期配置文件中的域名证书
python main.py renew

# 续期指定域名证书
python main.py renew -d example.com -d www.example.com
```

### 吊销证书

```bash
# 吊销配置文件中的域名证书
python main.py revoke

# 吊销指定域名证书
python main.py revoke -d example.com

# 指定吊销原因
python main.py revoke -d example.com -r 1
```

吊销原因代码：
- 0: unspecified（未指定）
- 1: keyCompromise（密钥泄露）
- 3: affiliationChanged（归属变更）
- 4: superseded（已替换）
- 5: cessationOfOperation（停止运营）

## 证书文件说明

颁发成功后，证书文件保存在 `certs/<domain>/` 目录下：

```
certs/example.com/
├── cert.pem         # 服务器证书
├── chain.pem        # 中间证书链
├── fullchain.pem    # 完整证书链（cert.pem + chain.pem）
└── privkey.pem      # 私钥
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
    ssl_prefer_server_ciphers on;
    
    # 其他配置...
}
```

重启Nginx：
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Apache

```apache
<VirtualHost *:443>
    ServerName example.com
    
    SSLEngine on
    SSLCertificateFile /path/to/certs/example.com/cert.pem
    SSLCertificateKeyFile /path/to/certs/example.com/privkey.pem
    SSLCertificateChainFile /path/to/certs/example.com/chain.pem
    
    # 其他配置...
</VirtualHost>
```

重启Apache：
```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

## 数据库SSL配置

### MySQL/MariaDB

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

确保私钥权限：
```bash
chown postgres:postgres /path/to/certs/example.com/privkey.pem
chmod 600 /path/to/certs/example.com/privkey.pem
```

### MongoDB

编辑 `mongod.conf`：

```yaml
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /path/to/certs/example.com/fullchain-with-key.pem
    CAFile: /path/to/certs/example.com/chain.pem
```

创建合并证书：
```bash
cat certs/example.com/fullchain.pem certs/example.com/privkey.pem > certs/example.com/fullchain-with-key.pem
chmod 600 certs/example.com/fullchain-with-key.pem
chown mongodb:mongodb certs/example.com/fullchain-with-key.pem
```

### Redis

编辑 `redis.conf`：

```ini
tls-port 6380
port 0
tls-cert-file /path/to/certs/example.com/cert.pem
tls-key-file /path/to/certs/example.com/privkey.pem
tls-ca-cert-file /path/to/certs/example.com/chain.pem
```

## 自动续期

### 使用Cron

创建续期脚本 `renew.sh`：

```bash
#!/bin/bash
cd /path/to/letsencrypt-dnsla
source venv/bin/activate
python main.py renew

# 重启服务（根据需要）
systemctl reload nginx
systemctl restart mysql
```

添加到crontab（每天凌晨3点检查）：

```bash
chmod +x renew.sh
crontab -e

# 添加以下行
0 3 * * * /path/to/letsencrypt-dnsla/renew.sh >> /var/log/cert-renew.log 2>&1
```

### 使用Systemd Timer（推荐）

创建服务文件 `/etc/systemd/system/cert-renew.service`：

```ini
[Unit]
Description=Renew Let's Encrypt Certificates
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/path/to/letsencrypt-dnsla
ExecStart=/path/to/letsencrypt-dnsla/venv/bin/python main.py renew
```

创建定时器 `/etc/systemd/system/cert-renew.timer`：

```ini
[Unit]
Description=Daily certificate renewal check

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

启用定时器：

```bash
sudo systemctl daemon-reload
sudo systemctl enable cert-renew.timer
sudo systemctl start cert-renew.timer

# 查看状态
sudo systemctl status cert-renew.timer
```

## 工作流程

证书颁发流程：

```
1. 生成证书私钥和CSR
2. 向Let's Encrypt创建订单
3. 获取DNS-01挑战
4. 通过DNS.LA API添加TXT记录
5. 等待DNS记录生效（默认120秒）
6. 提交挑战响应
7. Let's Encrypt验证DNS记录
8. 下载并保存证书
9. 清理DNS验证记录
```

## 故障排除

### 1. DNS API连接失败

**问题**：无法连接到DNS.LA API

**解决**：
- 检查API凭证是否正确
- 验证网络连接
- 确认DNS.LA服务状态

### 2. DNS验证超时

**问题**：Let's Encrypt无法验证DNS记录

**解决**：
- 增加 `propagation_seconds` 值（如180或300）
- 检查DNS.LA记录是否正确添加
- 使用 `dig` 或 `nslookup` 验证DNS记录：
  ```bash
  dig _acme-challenge.example.com TXT
  ```

### 3. 证书颁发失败

**问题**：达到速率限制

**解决**：
- 使用测试环境（`staging: true`）
- 等待一周后重试
- 查看 [Let's Encrypt速率限制文档](https://letsencrypt.org/docs/rate-limits/)

### 4. 权限错误

**问题**：无法写入证书文件

**解决**：
- 确保运行用户有写入 `cert_dir` 权限
- 使用 `sudo` 运行或修改目录权限

### 5. 模块导入错误

**问题**：`ModuleNotFoundError`

**解决**：
```bash
pip install -r requirements.txt --upgrade
```

## 安全建议

1. **保护私钥**：确保私钥文件权限为600
   ```bash
   chmod 600 certs/*/privkey.pem
   ```

2. **保护API凭证**：不要将 `config.yaml` 提交到公共仓库

3. **使用测试环境**：首次使用时启用 `staging: true`

4. **定期更新**：保持依赖包更新
   ```bash
   pip install -r requirements.txt --upgrade
   ```

5. **监控证书**：设置证书到期提醒

6. **备份证书**：定期备份 `certs/` 和 `accounts/` 目录

## Let's Encrypt 限制

- **有效期**：90天（建议30天前续期）
- **速率限制**：每周每域名50个证书
- **域名数量**：每个证书最多100个域名
- **通配符**：只支持一级通配符（*.example.com）

## 项目结构

```
letsencrypt-dnsla/
├── main.py              # 主程序入口
├── cert_manager.py      # 证书管理器
├── acme_client.py       # ACME客户端
├── dnsla_client.py      # DNS.LA API客户端
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 使用文档
├── accounts/           # 账户密钥目录
├── certs/              # 证书存储目录
└── letsencrypt.log     # 日志文件
```

## 依赖库

- `certbot` - Let's Encrypt官方客户端库
- `acme` - ACME协议实现
- `cryptography` - 加密库
- `requests` - HTTP客户端
- `josepy` - JOSE/JWT实现
- `pyyaml` - YAML配置解析

## 许可证

MIT License

## 相关资源

- [Let's Encrypt官网](https://letsencrypt.org/)
- [DNS.LA官网](https://www.dns.la)
- [Certbot文档](https://eff-certbot.readthedocs.io/)
- [ACME协议](https://tools.ietf.org/html/rfc8555)

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0 (2025-01-17)
- 初始版本发布
- 支持DNS-01验证
- 支持证书颁发、续期、吊销
- 集成DNS.LA API
