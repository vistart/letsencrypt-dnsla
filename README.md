# Let's Encrypt 证书管理工具（DNS.LA版本）

自动化Let's Encrypt证书颁发工具，使用DNS.LA API进行DNS-01验证。

## 系统要求

### Python 版本
- **Python 3.9+**（推荐 Python 3.10 或更高版本）
- 已在 Python 3.14 上测试通过

### 依赖库版本
- certbot >= 5.1.0
- acme >= 5.1.0
- cryptography >= 46.0.0
- requests >= 2.32.0
- pyyaml >= 6.0.3

完整依赖列表请查看 `requirements.txt`

### 其他要求
- pip（Python包管理器）
- 域名托管在DNS.LA
- 稳定的网络连接

## 特性

- ✅ 自动DNS-01验证（无需手动配置Web服务器）
- ✅ 支持单域名、多域名、通配符域名证书
- ✅ 自动DNS记录管理
- ✅ 证书查询、续期、吊销
- ✅ 智能账户管理（自动处理账户注册和复用）
- ✅ 零交互设计（适合自动化和CI/CD）
- ✅ 详细的日志记录
- ✅ 测试环境支持（避免触发速率限制）
- ✅ Python库实现，易于扩展

## 安装

### 1. 检查Python版本

```bash
python3 --version
# 确保版本 >= 3.9
```

### 2. 克隆或下载项目

```bash
git clone <repository-url>
cd letsencrypt-dnsla
```

### 3. 安装依赖

使用虚拟环境（强烈推荐）：

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

或直接安装：

```bash
pip install -r requirements.txt
```

### 4. 验证安装

```bash
python main.py --help
```

如果看到帮助信息，说明安装成功。

## 配置

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
      # - "*"  # 通配符

certificate:
  key_size: 2048
  renew_days: 30
```

### 获取DNS.LA API凭证

1. 登录 [DNS.LA](https://www.dns.la)
2. 进入"我的账户" -> "API密钥"
3. 获取 `APIID`（api_id）和 `APISecret`（api_secret）

⚠️ **重要提示**：如果在 DNS.LA 控制台中开启了"敏感操作"保护，请在使用本工具前暂时关闭，否则所有DNS记录修改操作（添加、删除验证记录）都会被拒绝，导致证书颁发失败。

### 获取域名ID

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

## 账户管理

本工具采用智能账户管理策略，完全支持零交互和自动化场景：

### 账户注册流程
1. **首次运行**：自动生成账户密钥并注册到 Let's Encrypt
2. **后续运行**：
   - 如果账户密钥存在且有效 → 直接使用
   - 如果账户密钥存在但账户不存在 → 使用现有密钥重新注册
   - 如果账户已注册 → 自动检测并复用

### 账户密钥存储
- 位置：`./accounts/account.key`
- 权限：自动设置为 600（仅所有者可读写）
- 环境隔离：测试环境和生产环境使用同一密钥但注册到不同服务器

### 定时任务和CI/CD
完全支持以下场景，无需人工干预：
- Cron 定时任务
- Systemd Timer
- CI/CD 流水线
- 容器化环境
- Kubernetes CronJob

示例：在 CI/CD 中使用
```yaml
# .gitlab-ci.yml
renew_certs:
  script:
    - python main.py renew
  schedule:
    - cron: "0 3 * * *"
```

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

服务器端配置：

```ini
[mysqld]
ssl-ca=/path/to/certs/example.com/chain.pem
ssl-cert=/path/to/certs/example.com/cert.pem
ssl-key=/path/to/certs/example.com/privkey.pem
require_secure_transport=ON
```

客户端连接（使用证书验证）：

```bash
mysql --host=example.com --port=3306 --user=username --password \
  --ssl-mode=VERIFY_IDENTITY \
  --ssl-ca=/path/to/certs/example.com/chain.pem \
  --ssl-cert=/path/to/certs/example.com/cert.pem \
  --ssl-key=/path/to/certs/example.com/privkey.pem \
  database_name
```

或者使用配置文件 `~/.my.cnf`：

```ini
[client]
ssl-ca=/path/to/certs/example.com/chain.pem
ssl-cert=/path/to/certs/example.com/cert.pem
ssl-key=/path/to/certs/example.com/privkey.pem
ssl-mode=VERIFY_IDENTITY
```

### PostgreSQL

服务器端配置：

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

客户端连接（使用证书验证）：

```bash
psql "host=example.com port=5432 dbname=database_name user=username sslmode=verify-full sslcert=/path/to/certs/example.com/cert.pem sslkey=/path/to/certs/example.com/privkey.pem sslrootcert=/path/to/certs/example.com/chain.pem"
```

或设置环境变量：

```bash
export PGSSLMODE=verify-full
export PGSSLROOTCERT=/path/to/certs/example.com/chain.pem
export PGSSLCERT=/path/to/certs/example.com/cert.pem
export PGSSLKEY=/path/to/certs/example.com/privkey.pem
psql -h example.com -p 5432 -U username -d database_name
```

### MongoDB

服务器端配置：

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

客户端连接（使用证书验证）：

```bash
mongosh --host example.com --port 27017 \
  --ssl --sslCAFile /path/to/certs/example.com/chain.pem \
  --sslPEMKeyFile /path/to/certs/example.com/fullchain-with-key.pem \
  --sslAllowInvalidCertificates false \
  --sslAllowInvalidHostnames false \
  mongodb://username@localhost:27017/database_name
```

### Redis

服务器端配置：

编辑 `redis.conf`：

```ini
tls-port 6380
port 0
tls-cert-file /path/to/certs/example.com/cert.pem
tls-key-file /path/to/certs/example.com/privkey.pem
tls-ca-cert-file /path/to/certs/example.com/chain.pem
```

客户端连接（使用证书验证）：

```bash
redis-cli -h example.com -p 6380 \
  --tls \
  --cacert /path/to/certs/example.com/chain.pem \
  --cert /path/to/certs/example.com/cert.pem \
  --key /path/to/certs/example.com/privkey.pem
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
1. 检查或创建 Let's Encrypt 账户
   - 如果账户密钥存在 → 加载密钥
   - 如果账户不存在 → 自动注册
   - 如果账户已存在 → 自动复用
2. 生成证书私钥和CSR
3. 向Let's Encrypt创建订单
4. 获取DNS-01挑战
5. 通过DNS.LA API添加TXT记录
6. 等待DNS记录生效（默认120秒）
7. 提交挑战响应
8. Let's Encrypt验证DNS记录
9. 下载并保存证书
10. 清理DNS验证记录
```

## 故障排除

### 1. DNS API连接失败

**问题**：无法连接到DNS.LA API

**解决**：
- 检查API凭证是否正确
- 验证网络连接
- 确认DNS.LA服务状态
- 确认未开启"敏感操作"保护

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

**问题**：`ModuleNotFoundError` 或版本不兼容

**解决**：
```bash
# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --upgrade

# 如果仍有问题，清理缓存后重装
pip cache purge
pip install -r requirements.txt --force-reinstall
```

### 6. 账户注册问题

**问题**：账户注册失败或重复注册

**说明**：本工具已实现智能账户管理，会自动处理以下情况：
- 账户不存在 → 自动注册
- 账户已存在 → 自动复用
- 密钥不匹配 → 使用现有密钥重新注册

如果仍有问题：
```bash
# 1. 查看日志
tail -f letsencrypt.log

# 2. 删除账户密钥后重试
rm -f accounts/account.key
python main.py issue

# 3. 切换环境测试
# 修改 config.yaml: staging: true
python main.py issue
```

## 版本兼容性

### Python 版本
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12
- ✅ Python 3.13
- ✅ Python 3.14
- ❌ Python 3.8 及以下（不支持）

### 主要依赖版本
| 库 | 最低版本 | 推荐版本 |
|---|---|---|
| certbot | 5.1.0 | 最新 |
| acme | 5.1.0 | 最新 |
| cryptography | 46.0.0 | 最新 |
| requests | 2.32.0 | 最新 |

### 更新依赖

定期更新依赖以获得最新功能和安全修复：

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

4. **关闭敏感操作保护**：使用本工具前，在 DNS.LA 控制台中暂时关闭"敏感操作"保护

5. **定期更新**：保持依赖包更新
   ```bash
   pip install -r requirements.txt --upgrade
   ```

6. **监控证书**：设置证书到期提醒

7. **备份证书**：定期备份 `certs/` 和 `accounts/` 目录

8. **账户密钥安全**：
   - 账户密钥存储在 `accounts/account.key`
   - 自动设置为 600 权限
   - 不要删除或泄露此文件
   - 建议备份到安全位置

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

### v1.1.0 (2025-10-17)
- 🎉 修复 CSR 生成逻辑，兼容 certbot/acme 5.1.0+
- 🎉 改进账户注册流程，支持零交互和自动化场景
- 🎉 智能账户管理：自动检测和复用已注册账户
- 🎉 更新依赖版本，支持 Python 3.14
- 📝 完善文档，增加版本兼容性说明
- 🐛 修复多个边界情况的异常处理

### v1.0.0 (2025-01-17)
- 初始版本发布
- 支持DNS-01验证
- 支持证书颁发、续期、吊销
- 集成DNS.LA API
