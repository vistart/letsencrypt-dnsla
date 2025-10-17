# Let's Encrypt 证书管理工具（DNS.LA版本）- 项目知识库

## 项目概述

这是一个使用DNS.LA API进行DNS-01验证的Let's Encrypt证书自动化管理工具。该项目完全使用Python实现，支持零交互自动化场景，适用于生产环境中的SSL证书管理。

## 核心功能

1. **自动DNS-01验证**：无需手动配置Web服务器
2. **多域名支持**：支持单域名、多域名、通配符域名证书
3. **DNS记录管理**：自动添加和删除验证记录
4. **证书全生命周期**：颁发、续期、吊销、查询
5. **智能账户管理**：自动处理Let's Encrypt账户注册和复用
6. **测试环境支持**：避免触发速率限制

## 项目结构

```
letsencrypt-dnsla/
├── main.py              # 主程序入口，包含命令行参数解析
├── cert_manager.py      # 证书管理器，整合DNS.LA和ACME客户端
├── acme_client.py       # ACME客户端，与Let's Encrypt交互
├── dnsla_client.py      # DNS.LA API客户端，管理DNS记录
├── config.yaml          # 配置文件模板
├── requirements.txt     # 依赖列表
└── letsencrypt.log      # 日志文件
```

## 核心组件

### 1. ACME客户端 (`acme_client.py`)

- 使用certbot库与Let's Encrypt API交互
- 实现智能账户管理：自动注册、获取已存在账户
- 支持生产环境和测试环境
- 生成CSR（证书签名请求）
- 处理DNS-01验证挑战

### 2. DNS.LA客户端 (`dnsla_client.py`)

- 封装DNS.LA API操作
- 支持添加、删除、更新DNS记录
- 专门的TXT记录管理功能（用于ACME验证）
- 智能记录更新策略（删除旧记录+添加新记录）

### 3. 证书管理器 (`cert_manager.py`)

- 协调ACME和DNS.LA客户端
- 实现完整的证书颁发流程
- 证书续期和吊销功能
- 证书信息查询和列表功能

### 4. 主程序 (`main.py`)

- 命令行参数解析
- 支持issue, renew, info, list, revoke, test-dns等命令
- 配置文件加载和日志设置

## 工作流程

### 证书颁发流程

1. 检查或创建Let's Encrypt账户
2. 生成证书私钥和CSR
3. 向Let's Encrypt创建订单
4. 获取DNS-01挑战
5. 通过DNS.LA API添加TXT验证记录
6. 等待DNS记录生效（默认120秒）
7. 提交挑战响应
8. Let's Encrypt验证DNS记录
9. 下载并保存证书
10. 清理DNS验证记录

### 智能账户管理

- **首次运行**：生成账户密钥并注册到Let's Encrypt
- **后续运行**：
  - 若账户密钥存在且有效 → 直接使用
  - 若账户密钥存在但账户不存在 → 用现有密钥重新注册
  - 若账户已存在 → 自动检测并复用

## 配置文件 (`config.yaml`)

```yaml
letsencrypt:
  staging: true         # 是否使用测试环境
  email: "your-email@example.com"  # Let's Encrypt联系邮箱
  cert_dir: "./certs"   # 证书存储目录
  account_dir: "./accounts"  # 账户密钥目录

dnsla:
  base_url: "https://api.dns.la"  # DNS.LA API基础URL
  api_id: "your_api_id"          # DNS.LA API ID
  api_secret: "your_api_secret"  # DNS.LA API密钥
  propagation_seconds: 120       # DNS记录生效等待时间

certificate:
  key_size: 2048      # RSA密钥大小
  renew_days: 30      # 证书到期前多少天开始续期
```

## 命令行使用

### 基本命令

```bash
# 颁发证书
python main.py issue [-d domain1 -d domain2 ...]

# 续期证书
python main.py renew [-d domain1 -d domain2 ...]

# 查看证书信息
python main.py info [-d domain] [-f cert_file]

# 列出所有证书
python main.py list

# 吊销证书
python main.py revoke [-d domain] [-f cert_file] [-r reason]

# 测试DNS API
python main.py test-dns
```

## 依赖库

- `certbot >= 5.1.0` - Let's Encrypt官方客户端库
- `acme >= 5.1.0` - ACME协议实现
- `cryptography >= 46.0.0` - 加密库
- `requests >= 2.32.0` - HTTP客户端
- `pyyaml >= 6.0.3` - YAML配置解析

## 证书文件结构

成功颁发后，证书文件保存在 `certs/<domain>/` 目录下：

```
cert.pem          # 服务器证书
chain.pem         # 中间证书链
fullchain.pem     # 完整证书链（cert.pem + chain.pem）
privkey.pem       # 私钥
```

## 自动续期配置

### Cron示例

```bash
# 每天凌晨3点检查证书续期
0 3 * * * /path/to/venv/bin/python /path/to/letsencrypt-dnsla/main.py renew >> /var/log/cert-renew.log 2>&1
```

### Systemd Timer示例

```
[Unit]
Description=Renew Let's Encrypt Certificates
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/path/to/letsencrypt-dnsla
ExecStart=/path/to/venv/bin/python main.py renew

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## 安全最佳实践

1. **文件权限**：证书私钥设为600权限
2. **API凭证**：不要将配置文件提交到公共仓库
3. **测试环境**：首次使用启用`staging: true`
4. **DNS.LA保护**：使用前关闭敏感操作保护
5. **定期更新**：保持依赖包更新

## 故障排除

### 常见问题

1. **DNS API连接失败**：检查API凭证和网络连接
2. **DNS验证超时**：增加`propagation_seconds`值
3. **速率限制**：使用测试环境
4. **权限错误**：确保写入目录权限
5. **模块导入错误**：重新安装依赖

### 调试方法

- 使用`-v`参数启用详细日志
- 查看`letsencrypt.log`文件
- 使用`test-dns`命令测试API连接

## 版本兼容性

- Python 3.9+（推荐3.10+）
- 已测试Python 3.14
- certbot/acme 5.1.0+（修复CSR生成逻辑）