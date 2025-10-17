# Let's Encrypt DNS.LA 自动化证书管理系统

## 项目概览

这是一个完整的Python项目，实现了Let's Encrypt证书的自动化管理，使用DNS.LA API进行DNS-01验证。

## 核心特性

✅ **自动化DNS验证** - 使用DNS.LA API自动添加和删除验证记录  
✅ **多域名支持** - 支持单域名、多域名、通配符域名证书  
✅ **完整的证书管理** - 颁发、查询、续期、吊销  
✅ **测试环境** - 支持Let's Encrypt测试环境，避免触发速率限制  
✅ **详细日志** - 完整的日志记录，便于调试  
✅ **模块化设计** - 清晰的代码结构，易于扩展  

## 项目结构

```
letsencrypt-dnsla/
├── main.py              # 主程序入口（命令行工具）
├── cert_manager.py      # 证书管理器（核心逻辑）
├── acme_client.py       # ACME客户端（与Let's Encrypt交互）
├── dnsla_client.py      # DNS.LA API客户端（DNS记录管理）
├── config.yaml          # 配置文件
├── requirements.txt     # Python依赖
├── install.sh           # 自动化安装脚本
├── examples.py          # 示例代码
├── README.md           # 详细使用文档
├── .gitignore          # Git忽略文件
├── accounts/           # Let's Encrypt账户密钥（自动生成）
├── certs/              # 证书存储目录（自动生成）
└── letsencrypt.log     # 运行日志（自动生成）
```

## 核心模块说明

### 1. dnsla_client.py - DNS.LA API客户端

**功能：**
- 域名信息查询
- DNS记录增删改查
- TXT记录管理（用于ACME验证）
- HTTP Basic Auth认证

**关键类：**
- `DNSLAClient` - DNS.LA API客户端主类

**主要方法：**
```python
# 获取域名信息
get_domain_info(domain)

# 获取DNS记录列表
get_record_list(domain_id, record_type, host, data)

# 添加/删除TXT记录
add_txt_record(domain_id, host, value, ttl)
delete_txt_records(domain_id, host)

# 更新TXT记录（删除+添加）
update_txt_record(domain_id, host, new_value, ttl)
```

### 2. acme_client.py - ACME客户端

**功能：**
- Let's Encrypt账户管理
- 证书订单创建
- DNS-01挑战处理
- 证书签发和保存

**关键类：**
- `ACMEClient` - ACME协议客户端

**主要方法：**
```python
# 创建订单并获取挑战
create_order(domains)

# 获取DNS挑战数据
get_dns_challenge_data(challenge)

# 提交挑战响应
answer_challenge(challenge)

# 轮询订单状态
poll_order(order, max_attempts)

# 生成和保存证书
generate_certificate(domains, cert_dir, key_size)
save_certificate(order, cert_path, domains)
```

### 3. cert_manager.py - 证书管理器

**功能：**
- 整合DNS客户端和ACME客户端
- 完整的证书颁发流程
- 证书信息查询
- 证书续期检查
- 证书吊销

**关键类：**
- `CertificateManager` - 证书管理主类

**主要方法：**
```python
# 颁发证书（完整流程）
issue_certificate(domains, cert_dir, key_size)

# 查询证书信息
get_certificate_info(cert_file)

# 检查是否需要续期
check_certificate_expiry(cert_file, renew_days)

# 续期证书
renew_certificate(domains, cert_dir, key_size, renew_days)

# 吊销证书
revoke_certificate(cert_file, reason)

# 列出所有证书
list_certificates(cert_dir)
```

### 4. main.py - 命令行工具

**功能：**
- 提供命令行接口
- 参数解析
- 配置文件加载
- 命令分发

**支持的命令：**
```bash
# 颁发证书
python main.py issue [-d DOMAIN ...]

# 续期证书
python main.py renew [-d DOMAIN ...]

# 查看证书信息
python main.py info [-d DOMAIN | -f CERT_FILE]

# 列出所有证书
python main.py list

# 吊销证书
python main.py revoke [-d DOMAIN | -f CERT_FILE] [-r REASON]

# 测试DNS API
python main.py test-dns
```

## 工作流程

### 证书颁发流程

```
1. 加载配置文件
   ↓
2. 初始化DNS.LA客户端和ACME客户端
   ↓
3. 生成证书私钥和CSR
   ↓
4. 向Let's Encrypt创建订单
   ↓
5. 获取DNS-01挑战
   ↓
6. 通过DNS.LA API添加TXT验证记录
   ↓
7. 等待DNS记录生效（默认120秒）
   ↓
8. 向Let's Encrypt提交挑战响应
   ↓
9. Let's Encrypt验证DNS记录
   ↓
10. 下载证书链
   ↓
11. 保存证书文件
   ↓
12. 清理DNS验证记录
   ↓
13. 完成
```

### DNS-01验证原理

1. **Let's Encrypt要求：** 在域名下创建特定的TXT记录
   ```
   记录名: _acme-challenge.example.com
   记录值: <随机生成的验证字符串>
   ```

2. **验证过程：**
   - Let's Encrypt查询DNS记录
   - 验证记录值是否匹配
   - 验证通过后签发证书

3. **自动化实现：**
   - 程序自动调用DNS.LA API添加TXT记录
   - 等待DNS传播
   - Let's Encrypt验证
   - 验证完成后自动删除记录

## 配置说明

### config.yaml 配置项

```yaml
# Let's Encrypt配置
letsencrypt:
  staging: true          # 测试环境（首次使用建议true）
  email: "admin@example.com"  # 联系邮箱
  cert_dir: "./certs"    # 证书存储目录
  account_dir: "./accounts"  # 账户密钥目录

# DNS.LA API配置
dnsla:
  base_url: "https://api.dns.la"  # API地址
  api_id: "your_api_id"           # API ID
  api_secret: "your_api_secret"   # API Secret
  propagation_seconds: 120        # DNS生效等待时间

# 域名配置
domains:
  - domain: "example.com"    # 主域名
    domain_id: "12345"       # DNS.LA域名ID
    subdomains:              # 子域名列表
      - "@"                  # 根域名
      - "www"                # www子域名
      # - "*"                # 通配符

# 证书配置
certificate:
  key_size: 2048          # RSA密钥大小
  renew_days: 30          # 提前续期天数
```

## 快速开始

### 1. 安装

```bash
# 克隆项目
cd letsencrypt-dnsla

# 运行安装脚本
chmod +x install.sh
./install.sh

# 或手动安装
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml`，填入你的信息：
- DNS.LA API凭证
- 域名和域名ID
- 邮箱地址

### 3. 测试

```bash
# 测试DNS API连接
python main.py test-dns
```

### 4. 颁发证书

```bash
# 使用测试环境（首次推荐）
python main.py issue

# 确认无误后，修改config.yaml中的staging为false
# 然后颁发正式证书
python main.py issue
```

## 使用场景

### 场景1: 单域名Web服务器

```bash
# 配置文件中设置
domains:
  - domain: "example.com"
    domain_id: "12345"
    subdomains:
      - "@"

# 颁发证书
python main.py issue

# Nginx配置
ssl_certificate /path/to/certs/example.com/fullchain.pem;
ssl_certificate_key /path/to/certs/example.com/privkey.pem;
```

### 场景2: 多域名证书

```bash
# 配置文件中设置
subdomains:
  - "@"
  - "www"
  - "api"
  - "blog"

# 一次性为所有子域名颁发证书
python main.py issue
```

### 场景3: 通配符证书

```bash
# 配置文件中设置
subdomains:
  - "@"
  - "*"

# 颁发通配符证书，覆盖所有子域名
python main.py issue
```

### 场景4: 数据库SSL

```bash
# 颁发证书
python main.py issue -d db.example.com

# MySQL配置
ssl-ca=/path/to/certs/db.example.com/chain.pem
ssl-cert=/path/to/certs/db.example.com/cert.pem
ssl-key=/path/to/certs/db.example.com/privkey.pem
```

### 场景5: 自动续期

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

# 添加到crontab（每天凌晨3点）
0 3 * * * /path/to/renew.sh >> /var/log/cert-renew.log 2>&1
```

## API参考

### DNSLAClient类

```python
from dnsla_client import DNSLAClient

# 初始化
client = DNSLAClient(
    api_id="your_api_id",
    api_secret="your_api_secret",
    base_url="https://api.dns.la"
)

# 获取域名信息
domain_info = client.get_domain_info("example.com")
print(domain_info['id'])  # 域名ID

# 添加TXT记录
record_id = client.add_txt_record(
    domain_id="12345",
    host="_acme-challenge",
    value="validation_string",
    ttl=600
)

# 删除记录
client.delete_record(record_id)
```

### ACMEClient类

```python
from acme_client import ACMEClient

# 初始化
acme = ACMEClient(
    email="admin@example.com",
    account_dir="./accounts",
    staging=True  # 测试环境
)

# 生成证书
cert_path, order, key = acme.generate_certificate(
    domains=["example.com"],
    cert_dir="./certs",
    key_size=2048
)
```

### CertificateManager类

```python
from cert_manager import CertificateManager
from dnsla_client import DNSLAClient
from acme_client import ACMEClient

# 初始化组件
dns = DNSLAClient(api_id="...", api_secret="...")
acme = ACMEClient(email="...", staging=True)

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
print(f"剩余天数: {info['days_remaining']}")

# 续期证书
manager.renew_certificate(
    domains=["example.com"],
    renew_days=30
)
```

## 常见问题

### Q: 为什么DNS验证要等待120秒？
A: DNS记录在全球传播需要时间，120秒是保守估计。如果验证失败，可以增加等待时间。

### Q: 可以一次申请多少个域名？
A: Let's Encrypt允许每个证书最多100个域名。

### Q: 通配符证书覆盖几级域名？
A: 只覆盖一级子域名。例如 `*.example.com` 覆盖 `www.example.com`，但不覆盖 `api.www.example.com`。

### Q: staging和production有什么区别？
A: staging是测试环境，速率限制宽松但证书不被浏览器信任；production是生产环境，签发正式证书但有严格的速率限制。

### Q: 证书多久会过期？
A: Let's Encrypt证书有效期90天，建议提前30天续期。

### Q: 如何撤销续期任务？
A: 使用 `crontab -e` 删除相应行，或 `systemctl disable cert-renew.timer` 停止systemd定时器。

## 技术细节

### HTTP Basic Auth计算

```python
import base64

api_id = "3731517a6e365a52776b3a003a31515330724c"
api_secret = "7ad4ca3e8fe258780397df3fd226e427cf884d83"

credentials = f"{api_id}:{api_secret}"
token = base64.b64encode(credentials.encode()).decode()
print(f"Authorization: Basic {token}")
```

### DNS记录修改策略

为确保DNS记录更新及时生效，本项目采用"删除+添加"而非"修改"的策略：

```python
# 不推荐：直接修改（生效慢）
update_record(record_id, new_value)

# 推荐：删除后添加（生效快）
delete_record(record_id)
add_record(host, new_value)
```

### 证书文件说明

```
cert.pem       - 服务器证书（单个）
chain.pem      - 中间证书链
fullchain.pem  - 完整证书链（cert.pem + chain.pem）
privkey.pem    - 私钥（RSA 2048位）
```

Web服务器推荐使用 `fullchain.pem`，数据库可能需要分别指定各个文件。

## 安全注意事项

1. **保护私钥** - privkey.pem权限应为600
2. **保护API凭证** - config.yaml不要提交到公共仓库
3. **使用测试环境** - 首次使用时启用staging避免触发速率限制
4. **定期备份** - 备份accounts/和certs/目录
5. **监控证书** - 设置证书到期提醒

## 性能优化

- DNS propagation时间可根据实际情况调整
- 使用Python虚拟环境避免依赖冲突
- 日志文件定期清理

## 贡献指南

欢迎提交Issue和Pull Request！

代码风格：
- 遵循PEP 8
- 使用类型提示
- 添加docstring文档
- 编写单元测试

## 许可证

MIT License

## 联系方式

- 项目主页: [GitHub]
- 问题反馈: [Issues]
- 邮箱: admin@example.com

---

**祝使用愉快！🎉**
