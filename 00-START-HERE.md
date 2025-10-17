# Let's Encrypt + DNS.LA 自动化证书管理系统

## 📦 项目包内容

这是一个完整的Python项目，实现Let's Encrypt证书的全自动化管理，使用DNS.LA API进行DNS-01验证。

**项目统计：**
- 总代码量：约4000行
- Python模块：4个核心模块
- 文档：5份详细文档（约45KB）
- 示例代码：8个实用示例

## 📂 文件清单

### 🔧 核心代码（4个文件，48KB）

| 文件 | 大小 | 说明 |
|------|------|------|
| `dnsla_client.py` | 11KB | DNS.LA API客户端，管理DNS记录 |
| `acme_client.py` | 11KB | ACME协议客户端，与Let's Encrypt交互 |
| `cert_manager.py` | 14KB | 证书管理器，核心业务逻辑 |
| `main.py` | 12KB | 命令行工具，用户入口 |

### 📖 文档（5个文件，45KB）

| 文件 | 大小 | 说明 |
|------|------|------|
| `README.md` | 10KB | 完整使用指南和故障排除 |
| `PROJECT_OVERVIEW.md` | 12KB | 项目架构、模块说明、API参考 |
| `QUICK_REFERENCE.md` | 7KB | 命令速查表和配置模板 |
| `SUMMARY.md` | 8KB | 项目总结和快速开始 |
| `CHECKLIST.md` | 6KB | 部署检查清单 |

### 🎯 示例和工具（3个文件，13KB）

| 文件 | 大小 | 说明 |
|------|------|------|
| `examples.py` | 8KB | 8个实用代码示例 |
| `install.sh` | 5KB | 自动化安装脚本 |
| `config.yaml` | 1KB | 配置文件模板 |

### 📋 其他文件

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python依赖列表 |
| `.gitignore` | Git忽略文件配置 |
| `00-START-HERE.md` | 本文件 |

## 🚀 快速开始（3步）

### 第1步：安装依赖

```bash
# 进入项目目录
cd letsencrypt-dnsla

# 运行安装脚本（推荐）
chmod +x install.sh
./install.sh

# 或手动安装
pip install -r requirements.txt
```

### 第2步：配置

编辑 `config.yaml`，填入你的信息：

```yaml
letsencrypt:
  staging: true  # ⚠️ 首次使用务必设为true
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

### 第3步：颁发证书

```bash
# 测试DNS API
python main.py test-dns

# 颁发证书（测试环境）
python main.py issue

# 查看证书信息
python main.py info
```

## 📚 文档导航

根据你的需求选择阅读：

### 🆕 新手入门
1. **START-HERE.md** (本文件) - 5分钟快速上手
2. **SUMMARY.md** - 项目总结和使用场景
3. **README.md** - 详细的安装和使用指南

### 💻 日常使用
- **QUICK_REFERENCE.md** - 命令速查表
- **examples.py** - 代码示例

### 🔧 深入了解
- **PROJECT_OVERVIEW.md** - 技术架构和API文档
- **CHECKLIST.md** - 部署检查清单

### 📖 推荐阅读顺序

**完全新手：**
```
START-HERE.md → README.md → QUICK_REFERENCE.md → 开始使用
```

**有经验用户：**
```
SUMMARY.md → QUICK_REFERENCE.md → 开始使用
```

**开发人员：**
```
PROJECT_OVERVIEW.md → examples.py → 开始开发
```

## ⚡ 主要命令

```bash
# 测试DNS API连接
python main.py test-dns

# 颁发证书
python main.py issue

# 查看证书信息
python main.py info

# 列出所有证书
python main.py list

# 续期证书
python main.py renew

# 吊销证书
python main.py revoke -d example.com

# 查看帮助
python main.py --help
```

## 🎯 核心特性

✅ **完全自动化** - DNS验证、证书下载、记录清理全自动  
✅ **支持通配符** - 可为 `*.rho.im` 颁发证书  
✅ **易于使用** - 简单的命令行工具  
✅ **功能完整** - 颁发、查询、续期、吊销  
✅ **安全可靠** - 使用Let's Encrypt官方库  
✅ **详细文档** - 45KB+文档和示例  

## 🔐 安全提醒

⚠️ **重要：首次使用务必启用测试环境**
```yaml
letsencrypt:
  staging: true  # 测试环境
```

测试成功后再修改为 `false` 申请正式证书。

⚠️ **保护敏感信息：**
```bash
chmod 600 config.yaml
chmod 600 certs/*/privkey.pem
```

## 🌟 使用场景

### Web服务器HTTPS
```nginx
# Nginx配置
ssl_certificate /path/to/certs/rho.im/fullchain.pem;
ssl_certificate_key /path/to/certs/rho.im/privkey.pem;
```

### 数据库SSL
```ini
# MySQL配置
ssl-ca=/path/to/certs/rho.im/chain.pem
ssl-cert=/path/to/certs/rho.im/cert.pem
ssl-key=/path/to/certs/rho.im/privkey.pem
```

### 通配符证书
```bash
# 一次性为所有子域名颁发证书
python main.py issue -d rho.im -d "*.rho.im"
```

## 🆘 获取帮助

### 查看日志
```bash
tail -f letsencrypt.log
```

### 常见问题
1. **DNS API连接失败** → 检查config.yaml中的API凭证
2. **DNS验证超时** → 增加 `propagation_seconds` 值
3. **触发速率限制** → 使用测试环境（staging: true）

### 详细故障排查
参见 `README.md` 的"故障排除"章节

## 📞 资源链接

- **Let's Encrypt**: https://letsencrypt.org
- **DNS.LA**: https://www.dns.la
- **Certbot文档**: https://eff-certbot.readthedocs.io

## ✅ 快速检查清单

部署前确认：
- [ ] Python 3.7+ 已安装
- [ ] 已获取DNS.LA API凭证
- [ ] 已知道域名ID
- [ ] config.yaml已正确配置
- [ ] staging设为true（首次使用）
- [ ] 已运行 `python main.py test-dns` 测试

部署后确认：
- [ ] 证书成功颁发
- [ ] Web服务器/数据库已配置
- [ ] HTTPS访问正常
- [ ] 已设置自动续期

## 🎉 开始使用

```bash
# 1. 进入目录
cd letsencrypt-dnsla

# 2. 安装
./install.sh

# 3. 测试
python main.py test-dns

# 4. 颁发证书
python main.py issue

# 5. 查看结果
python main.py info
```

## 💡 提示

- 📖 遇到问题先查看 `README.md` 的故障排除章节
- 🔍 使用 `python main.py --help` 查看所有命令
- 📝 查看 `letsencrypt.log` 获取详细信息
- ⚠️ 首次使用务必启用测试环境

## 🚀 下一步

1. ✅ 阅读本文件（你已经在做了）
2. 📖 快速浏览 `SUMMARY.md` 了解项目
3. 🔧 运行 `./install.sh` 安装依赖
4. ⚙️ 编辑 `config.yaml` 配置信息
5. 🧪 运行 `python main.py test-dns` 测试
6. 🎯 运行 `python main.py issue` 颁发证书
7. 📚 参考 `QUICK_REFERENCE.md` 日常使用

---

**准备好了吗？开始你的自动化证书管理之旅！** 🎊

有任何问题，请参考相应的文档文件。祝使用愉快！
