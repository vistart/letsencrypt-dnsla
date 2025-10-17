# Let's Encrypt DNS.LA 自动化证书管理系统

## 项目说明

这是一个完整的Python项目，实现了Let's Encrypt证书的全自动化管理，使用DNS.LA API进行DNS-01验证。无需手动配置Web服务器，完全通过DNS记录验证域名所有权。

## ✨ 核心优势

1. **完全自动化** - 从DNS验证到证书下载，无需人工介入
2. **安全可靠** - 使用Let's Encrypt官方Python库（certbot/acme）
3. **易于使用** - 简单的命令行工具和详细的文档
4. **功能完整** - 支持颁发、查询、续期、吊销等所有操作
5. **支持通配符** - 可以为 *.example.com 颁发证书
6. **模块化设计** - 清晰的代码结构，易于理解和扩展

## 📦 项目文件

### 核心代码（4个Python文件）

1. **dnsla_client.py** (11KB)
   - DNS.LA API客户端
   - 管理DNS记录（增删改查）
   - 自动计算HTTP Basic Auth
   - TXT记录操作（用于ACME验证）

2. **acme_client.py** (11KB)
   - ACME协议客户端
   - 与Let's Encrypt交互
   - 账户管理和证书签发
   - DNS-01挑战处理

3. **cert_manager.py** (14KB)
   - 证书管理核心逻辑
   - 整合DNS和ACME客户端
   - 完整的证书生命周期管理
   - 证书信息查询和续期检查

4. **main.py** (12KB)
   - 命令行工具入口
   - 参数解析和命令分发
   - 配置文件加载
   - 友好的用户界面

### 配置和文档

5. **config.yaml** - 配置文件模板
6. **requirements.txt** - Python依赖列表
7. **README.md** (10KB) - 完整使用文档
8. **PROJECT_OVERVIEW.md** (12KB) - 项目概览和技术细节
9. **QUICK_REFERENCE.md** (8KB) - 快速参考和命令速查
10. **examples.py** (8KB) - 代码示例

### 辅助文件

11. **install.sh** (5KB) - 自动化安装脚本
12. **.gitignore** - Git忽略文件（保护敏感信息）

## 🚀 快速开始

### 1. 安装

```bash
cd letsencrypt-dnsla
./install.sh
```

或手动安装：
```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml`：

```yaml
letsencrypt:
  staging: true  # 首次使用建议true
  email: "admin@rho.im"

dnsla:
  api_id: "3731517a6e365a52776b3a003a31515330724c"
  api_secret: "7ad4ca3e8fe258780397df3fd226e427cf884d83"

domains:
  - domain: "rho.im"
    domain_id: "5435272"
    subdomains:
      - "@"
```

### 3. 测试

```bash
python main.py test-dns
```

### 4. 颁发证书

```bash
# 测试环境（staging: true）
python main.py issue

# 确认无误后，修改config.yaml中staging为false
# 颁发正式证书
python main.py issue
```

## 📝 主要功能

### 证书颁发
```bash
# 使用配置文件
python main.py issue

# 指定域名
python main.py issue -d rho.im -d www.rho.im

# 通配符证书
python main.py issue -d rho.im -d "*.rho.im"
```

### 证书查询
```bash
# 查看证书信息
python main.py info

# 列出所有证书
python main.py list
```

### 证书续期
```bash
# 自动续期（检查是否到期）
python main.py renew
```

### 证书吊销
```bash
# 吊销证书
python main.py revoke -d rho.im
```

## 🔧 工作原理

### DNS-01验证流程

```
1. 向Let's Encrypt创建证书订单
2. 获取DNS-01挑战：需要创建特定的TXT记录
3. 通过DNS.LA API自动添加TXT记录
   记录名: _acme-challenge.rho.im
   记录值: <随机验证字符串>
4. 等待DNS记录全球传播（120秒）
5. 通知Let's Encrypt开始验证
6. Let's Encrypt查询DNS记录
7. 验证成功后签发证书
8. 下载并保存证书
9. 自动清理DNS验证记录
```

### 为什么选择DNS-01验证？

- ✅ 支持通配符证书（*.rho.im）
- ✅ 无需开放HTTP/HTTPS端口
- ✅ 无需配置Web服务器
- ✅ 适合内网服务器
- ✅ 适合数据库等非Web服务

### 关键技术点

1. **HTTP Basic Auth计算**
   ```python
   credentials = f"{api_id}:{api_secret}"
   token = base64.b64encode(credentials.encode()).decode()
   # Authorization: Basic <token>
   ```

2. **DNS记录更新策略**
   - 采用"删除+添加"而非"修改"
   - 确保DNS记录及时生效

3. **证书文件结构**
   ```
   cert.pem       - 服务器证书
   chain.pem      - 中间证书链
   fullchain.pem  - 完整证书链
   privkey.pem    - 私钥（RSA 2048位）
   ```

## 💻 使用场景

### 场景1: Web服务器HTTPS

**Nginx配置：**
```nginx
ssl_certificate /path/to/certs/rho.im/fullchain.pem;
ssl_certificate_key /path/to/certs/rho.im/privkey.pem;
```

### 场景2: 数据库SSL

**MySQL配置：**
```ini
ssl-ca=/path/to/certs/rho.im/chain.pem
ssl-cert=/path/to/certs/rho.im/cert.pem
ssl-key=/path/to/certs/rho.im/privkey.pem
```

**PostgreSQL配置：**
```ini
ssl = on
ssl_cert_file = '/path/to/certs/rho.im/cert.pem'
ssl_key_file = '/path/to/certs/rho.im/privkey.pem'
```

### 场景3: 通配符证书

一次性为所有子域名颁发证书：
```bash
python main.py issue -d rho.im -d "*.rho.im"
```

可以覆盖：
- api.rho.im
- blog.rho.im
- mail.rho.im
- 等所有一级子域名

### 场景4: 自动续期

创建续期脚本并添加到crontab：
```bash
#!/bin/bash
cd /path/to/letsencrypt-dnsla
source venv/bin/activate
python main.py renew
systemctl reload nginx
```

## 📚 文档说明

- **README.md** - 完整的安装和使用指南，包含故障排除
- **PROJECT_OVERVIEW.md** - 项目架构、模块说明、API参考
- **QUICK_REFERENCE.md** - 命令速查表和配置模板
- **examples.py** - 8个实用代码示例

## 🔐 安全建议

1. **保护私钥**
   ```bash
   chmod 600 certs/*/privkey.pem
   ```

2. **保护配置文件**
   ```bash
   chmod 600 config.yaml
   ```

3. **使用测试环境**
   - 首次使用时设置 `staging: true`
   - 避免触发Let's Encrypt速率限制
   - 测试成功后再使用生产环境

4. **定期备份**
   - 备份 `accounts/` 目录（账户密钥）
   - 备份 `certs/` 目录（证书文件）

5. **监控证书**
   - 设置证书到期提醒
   - 定期检查自动续期任务

## ⚙️ 技术栈

- **Python 3.7+**
- **certbot** - Let's Encrypt官方客户端库
- **acme** - ACME协议实现
- **cryptography** - 加密库
- **requests** - HTTP客户端
- **josepy** - JOSE/JWT实现
- **pyyaml** - 配置解析

## 📊 项目统计

- **代码行数**: ~2000行Python代码
- **文档**: 30KB+ 详细文档
- **模块**: 4个核心模块
- **功能**: 颁发、查询、续期、吊销
- **支持的域名类型**: 单域名、多域名、通配符
- **验证方式**: DNS-01

## 🎯 适用场景

✅ 需要为多个子域名颁发证书  
✅ 需要通配符证书（*.example.com）  
✅ 服务器在内网，无法使用HTTP验证  
✅ 需要为数据库等非Web服务配置SSL  
✅ 需要自动化证书管理  
✅ 域名托管在DNS.LA  

## ⚠️ 注意事项

1. **Let's Encrypt限制**
   - 证书有效期：90天
   - 速率限制：每周每域名50个证书
   - 建议提前30天续期

2. **DNS传播时间**
   - 默认等待120秒
   - 如果验证失败，可以增加等待时间
   - 配置项：`propagation_seconds`

3. **测试环境**
   - 首次使用务必启用 `staging: true`
   - 测试证书不被浏览器信任
   - 测试成功后再申请正式证书

4. **API凭证**
   - 从DNS.LA获取API ID和Secret
   - 不要将config.yaml提交到公共仓库
   - 使用.gitignore保护敏感信息

## 🆘 故障排查

### DNS API连接失败
```bash
# 测试API连接
python main.py test-dns

# 检查API凭证
# 确认config.yaml中的api_id和api_secret正确
```

### DNS验证超时
```bash
# 增加等待时间
# config.yaml中修改：propagation_seconds: 300

# 手动验证DNS记录
dig _acme-challenge.rho.im TXT
```

### 触发速率限制
```bash
# 使用测试环境
# config.yaml中设置：staging: true

# 或等待一周后重试
```

## 📞 获取帮助

```bash
# 查看帮助
python main.py --help

# 查看子命令帮助
python main.py issue --help
python main.py renew --help

# 查看日志
tail -f letsencrypt.log
```

## 🎉 开始使用

```bash
# 1. 安装
./install.sh

# 2. 测试
python main.py test-dns

# 3. 颁发证书
python main.py issue

# 4. 配置Web服务器或数据库
# 参考README.md中的配置示例

# 5. 设置自动续期
# 参考README.md中的Cron配置
```

## 📖 相关资源

- **Let's Encrypt官网**: https://letsencrypt.org
- **DNS.LA官网**: https://www.dns.la
- **Certbot文档**: https://eff-certbot.readthedocs.io
- **ACME协议**: https://tools.ietf.org/html/rfc8555

## 📄 许可证

MIT License

---

**享受自动化证书管理的便利！** 🚀
