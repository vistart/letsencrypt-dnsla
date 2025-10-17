# Let's Encrypt 证书申请脚本使用指南

## 概述

这是一个全自动的Let's Encrypt证书申请和管理脚本，支持macOS和Linux系统，可用于Web HTTPS和数据库SSL/TLS连接。

## 特性

- ✅ 支持单域名、多域名、通配符域名证书
- ✅ 三种验证方式：HTTP-01 (webroot/standalone)、DNS-01
- ✅ 自动安装和配置certbot
- ✅ 导出数据库兼容格式证书
- ✅ 自动续期配置
- ✅ 详细的日志记录
- ✅ 彩色输出，易于查看

## 前置要求

### 系统要求
- macOS 10.13+ 或 Linux (Ubuntu/Debian/CentOS/RHEL)
- Bash 4.0+
- sudo权限（部分操作需要）

### 域名控制
- 拥有域名的完整控制权
- 能够配置DNS记录（通配符证书必需）
- 能够访问Web服务器根目录（HTTP验证）

### DNS插件（通配符证书需要）

如需申请通配符证书，需要安装对应的DNS插件：

```bash
# Cloudflare
pip install certbot-dns-cloudflare

# AWS Route53
pip install certbot-dns-route53

# 阿里云DNS
pip install certbot-dns-aliyun

# 腾讯云DNSPod
pip install certbot-dns-dnspod

# Google Cloud DNS
pip install certbot-dns-google
```

## 快速开始

### 1. 下载并设置脚本权限

```bash
chmod +x letsencrypt-cert-manager.sh
```

### 2. 查看帮助信息

```bash
./letsencrypt-cert-manager.sh --help
```

### 3. 申请证书

根据你的需求选择合适的方式：

#### 方式一：单域名证书（Webroot验证）

最常用的方式，适合已有运行中的Web服务器：

```bash
./letsencrypt-cert-manager.sh \
  -d example.com \
  -m admin@example.com \
  -p /var/www/html
```

#### 方式二：多域名证书

一个证书包含多个域名：

```bash
./letsencrypt-cert-manager.sh \
  -d example.com \
  -d www.example.com \
  -d api.example.com \
  -m admin@example.com \
  -p /var/www/html
```

#### 方式三：通配符证书（DNS验证）

适合需要为所有子域名签发证书：

```bash
./letsencrypt-cert-manager.sh \
  -d example.com \
  -w \
  -m admin@example.com \
  --dns-plugin cloudflare
```

**注意**：使用DNS验证前需要配置DNS提供商的API凭证。

#### 方式四：Standalone模式

临时停止Web服务器使用：

```bash
# 先停止现有Web服务器
sudo systemctl stop nginx

# 申请证书
./letsencrypt-cert-manager.sh \
  -d example.com \
  -m admin@example.com \
  --standalone

# 重启Web服务器
sudo systemctl start nginx
```

#### 方式五：为数据库申请证书

导出数据库兼容格式：

```bash
./letsencrypt-cert-manager.sh \
  -d db.example.com \
  -m admin@example.com \
  -p /var/www/html \
  --export-db
```

## DNS插件配置

### Cloudflare配置

1. 创建配置文件 `~/.secrets/cloudflare.ini`：

```ini
dns_cloudflare_api_token = your_api_token_here
```

2. 设置权限：

```bash
chmod 600 ~/.secrets/cloudflare.ini
```

3. 申请证书时指定配置文件：

```bash
export CLOUDFLARE_CREDENTIALS=~/.secrets/cloudflare.ini
./letsencrypt-cert-manager.sh \
  -d example.com \
  -w \
  -m admin@example.com \
  --dns-plugin cloudflare
```

### Route53配置

确保AWS凭证已配置：

```bash
# 使用AWS CLI配置
aws configure

# 或设置环境变量
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## 证书文件说明

申请成功后，证书文件位于：`/etc/letsencrypt/live/your-domain/`

### Web服务器使用的文件

- **fullchain.pem** - 完整证书链（推荐用于Nginx）
- **cert.pem** - 服务器证书
- **chain.pem** - 中间证书
- **privkey.pem** - 私钥

### 数据库使用的文件（使用 --export-db 选项）

导出目录：`./db-certs/`

- **server-cert.pem** - 服务器证书
- **server-key.pem** - 私钥
- **ca-bundle.pem** - CA证书链
- **server-combined.pem** - MongoDB用合并证书

## Web服务器配置

### Nginx配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    # 推荐的SSL配置
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

### Apache配置

```apache
<VirtualHost *:443>
    ServerName example.com
    
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/example.com/chain.pem
    
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

编辑 `my.cnf`：

```ini
[mysqld]
ssl-ca=/path/to/db-certs/ca-bundle.pem
ssl-cert=/path/to/db-certs/server-cert.pem
ssl-key=/path/to/db-certs/server-key.pem
require_secure_transport=ON

[client]
ssl-ca=/path/to/db-certs/ca-bundle.pem
ssl-cert=/path/to/db-certs/server-cert.pem
ssl-key=/path/to/db-certs/server-key.pem
```

重启MySQL：
```bash
sudo systemctl restart mysql
```

验证SSL：
```sql
SHOW VARIABLES LIKE '%ssl%';
```

### PostgreSQL

编辑 `postgresql.conf`：

```ini
ssl = on
ssl_ca_file = '/path/to/db-certs/ca-bundle.pem'
ssl_cert_file = '/path/to/db-certs/server-cert.pem'
ssl_key_file = '/path/to/db-certs/server-key.pem'
```

确保私钥权限：
```bash
chown postgres:postgres /path/to/db-certs/server-key.pem
chmod 600 /path/to/db-certs/server-key.pem
```

重启PostgreSQL：
```bash
sudo systemctl restart postgresql
```

验证SSL：
```sql
SELECT ssl, version FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

### MongoDB

编辑 `mongod.conf`：

```yaml
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /path/to/db-certs/server-combined.pem
    CAFile: /path/to/db-certs/ca-bundle.pem
```

确保权限：
```bash
chown mongodb:mongodb /path/to/db-certs/server-combined.pem
chmod 600 /path/to/db-certs/server-combined.pem
```

重启MongoDB：
```bash
sudo systemctl restart mongod
```

连接测试：
```bash
mongo --tls --host example.com --tlsCAFile /path/to/db-certs/ca-bundle.pem
```

### Redis

编辑 `redis.conf`：

```ini
tls-port 6380
port 0
tls-cert-file /path/to/db-certs/server-cert.pem
tls-key-file /path/to/db-certs/server-key.pem
tls-ca-cert-file /path/to/db-certs/ca-bundle.pem
tls-auth-clients no
```

重启Redis：
```bash
sudo systemctl restart redis
```

连接测试：
```bash
redis-cli --tls --cacert /path/to/db-certs/ca-bundle.pem -h example.com -p 6380
```

## 证书续期

### 自动续期

脚本会自动配置certbot的续期任务。Let's Encrypt证书有效期为90天，certbot会在到期前30天自动续期。

查看续期任务（Linux）：
```bash
systemctl list-timers | grep certbot
```

或查看crontab：
```bash
sudo crontab -l | grep certbot
```

### 手动续期

测试续期（不实际续期）：
```bash
sudo certbot renew --dry-run
```

强制续期：
```bash
sudo certbot renew --force-renewal
```

### 续期后的操作

证书续期后，需要重新加载服务：

创建续期钩子 `/etc/letsencrypt/renewal-hooks/deploy/reload-services.sh`：

```bash
#!/bin/bash

# 重新导出数据库证书
CERT_PATH="/etc/letsencrypt/live/your-domain"
DB_CERT_PATH="/path/to/db-certs"

cp "$CERT_PATH/fullchain.pem" "$DB_CERT_PATH/server-cert.pem"
cp "$CERT_PATH/privkey.pem" "$DB_CERT_PATH/server-key.pem"
cp "$CERT_PATH/chain.pem" "$DB_CERT_PATH/ca-bundle.pem"
cat "$DB_CERT_PATH/server-cert.pem" "$DB_CERT_PATH/server-key.pem" > "$DB_CERT_PATH/server-combined.pem"

# 设置权限
chmod 644 "$DB_CERT_PATH/server-cert.pem"
chmod 600 "$DB_CERT_PATH/server-key.pem"
chmod 644 "$DB_CERT_PATH/ca-bundle.pem"
chmod 600 "$DB_CERT_PATH/server-combined.pem"
chown mongodb:mongodb "$DB_CERT_PATH/server-combined.pem"

# 重启服务
systemctl reload nginx
systemctl restart mysql
systemctl restart postgresql
systemctl restart mongod
systemctl restart redis
```

设置权限：
```bash
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-services.sh
```

## Let's Encrypt 限制说明

### 证书属性限制

Let's Encrypt有以下固定属性，**无法自定义**：

- **组织名（O）**：自动为空或 "Let's Encrypt"
- **组织单位（OU）**：不包含此字段
- **有效期**：固定90天
- **颁发机构**：Let's Encrypt Authority

### 使用限制

- **速率限制**：每个域名每周最多50个证书
- **域名数量**：每个证书最多100个域名
- **通配符**：只能是一级通配符（*.example.com）
- **IPv4地址**：不支持为IP地址签发证书

### 测试模式

首次使用建议加上 `--staging` 参数，使用测试服务器避免触发速率限制：

```bash
./letsencrypt-cert-manager.sh \
  -d example.com \
  -m admin@example.com \
  -p /var/www/html \
  --staging
```

测试成功后，去掉 `--staging` 参数重新申请正式证书。

## 常见问题

### 1. 权限错误

**问题**：`Permission denied`

**解决**：使用sudo运行脚本或切换到root用户

```bash
sudo ./letsencrypt-cert-manager.sh ...
```

### 2. 端口被占用（Standalone模式）

**问题**：`Problem binding to port 80/443`

**解决**：停止占用端口的服务

```bash
# 查看占用端口的进程
sudo lsof -i :80
sudo lsof -i :443

# 停止Nginx
sudo systemctl stop nginx

# 或停止Apache
sudo systemctl stop apache2
```

### 3. DNS验证失败

**问题**：DNS记录验证超时

**解决**：
- 检查DNS插件配置是否正确
- 确认API token有足够权限
- 检查防火墙是否阻止DNS查询
- 等待DNS记录传播（可能需要几分钟）

### 4. Webroot路径错误

**问题**：无法在webroot目录创建验证文件

**解决**：
- 确认webroot路径正确
- 检查目录权限（需要写入权限）
- 确认Web服务器配置了正确的根目录

### 5. 数据库无法启动

**问题**：配置SSL后数据库启动失败

**解决**：
- 检查证书文件路径是否正确
- 确认文件权限（私钥需要600权限）
- 确认文件所有者正确（如mongodb:mongodb）
- 查看数据库日志获取详细错误

### 6. 证书验证失败

测试证书是否有效：

```bash
# Web服务器
openssl s_client -connect example.com:443 -servername example.com

# MySQL
mysql --ssl-mode=REQUIRED --ssl-ca=/path/to/ca-bundle.pem -h example.com -u user -p

# PostgreSQL
psql "sslmode=require sslrootcert=/path/to/ca-bundle.pem host=example.com user=postgres"
```

## 脚本参数参考

| 参数 | 说明 | 必需 | 示例 |
|------|------|------|------|
| `-d, --domain` | 域名（可多次使用） | 是 | `-d example.com` |
| `-w, --wildcard` | 申请通配符证书 | 否 | `-w` |
| `-m, --email` | 联系邮箱 | 是 | `-m admin@example.com` |
| `-p, --webroot` | Webroot路径 | 否* | `-p /var/www/html` |
| `--standalone` | Standalone模式 | 否* | `--standalone` |
| `--dns-plugin` | DNS插件名称 | 否* | `--dns-plugin cloudflare` |
| `--export-db` | 导出数据库格式 | 否 | `--export-db` |
| `--cert-name` | 证书名称 | 否 | `--cert-name my-cert` |
| `--staging` | 测试模式 | 否 | `--staging` |
| `-h, --help` | 显示帮助 | 否 | `-h` |

*注：必须选择一种验证方式（webroot、standalone或dns-plugin）

## 安全建议

1. **私钥保护**：确保私钥文件权限为600，只有服务进程能读取
2. **定期更新**：保持certbot和系统更新到最新版本
3. **监控到期**：设置证书到期提醒
4. **备份证书**：定期备份 `/etc/letsencrypt` 目录
5. **强制HTTPS**：配置HTTP到HTTPS的重定向
6. **HSTS配置**：启用HTTP Strict Transport Security

## 日志查看

脚本运行日志保存在：`./letsencrypt.log`

查看certbot日志：
```bash
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

## 卸载清理

如需完全移除：

```bash
# 删除证书
sudo certbot delete --cert-name your-domain

# 卸载certbot (Ubuntu/Debian)
sudo apt-get remove --purge certbot

# 卸载certbot (macOS)
brew uninstall certbot

# 删除配置目录
sudo rm -rf /etc/letsencrypt
```

## 相关资源

- [Let's Encrypt官网](https://letsencrypt.org/)
- [Certbot文档](https://eff-certbot.readthedocs.io/)
- [速率限制说明](https://letsencrypt.org/docs/rate-limits/)
- [DNS插件列表](https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins)

## 支持与反馈

如有问题或建议，请查看：
- Let's Encrypt社区论坛
- Certbot GitHub Issues
- 各DNS插件的官方文档

---

**注意**：本脚本仅用于简化Let's Encrypt证书申请流程，实际使用时请根据具体环境调整配置。
