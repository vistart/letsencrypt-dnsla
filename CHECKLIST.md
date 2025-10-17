# 项目检查清单

## ✅ 文件完整性检查

### 核心代码文件
- [x] dnsla_client.py - DNS.LA API客户端
- [x] acme_client.py - ACME协议客户端  
- [x] cert_manager.py - 证书管理器
- [x] main.py - 命令行工具入口

### 配置文件
- [x] config.yaml - 配置文件模板
- [x] requirements.txt - Python依赖列表

### 文档文件
- [x] README.md - 完整使用文档
- [x] PROJECT_OVERVIEW.md - 项目概览
- [x] QUICK_REFERENCE.md - 快速参考
- [x] SUMMARY.md - 项目总结
- [x] CHECKLIST.md - 本检查清单

### 示例和脚本
- [x] examples.py - 代码示例
- [x] install.sh - 安装脚本

### 其他文件
- [x] .gitignore - Git忽略文件

## 📝 使用前检查

### 环境准备
- [ ] Python 3.7+ 已安装
- [ ] pip 已安装
- [ ] 网络连接正常

### DNS.LA准备
- [ ] 已有DNS.LA账户
- [ ] 域名已托管在DNS.LA
- [ ] 已获取API ID和API Secret
- [ ] 已知道域名ID

### 配置文件
- [ ] 已复制config.yaml并填写正确信息
- [ ] 邮箱地址已填写
- [ ] API凭证已填写
- [ ] 域名和域名ID已填写
- [ ] staging设置为true（首次使用）

## 🔧 安装检查

### 依赖安装
- [ ] 运行 `pip install -r requirements.txt`
- [ ] 所有依赖安装成功
- [ ] 无错误或警告信息

### 目录创建
- [ ] certs/ 目录存在
- [ ] accounts/ 目录存在

### 权限设置
- [ ] install.sh 有执行权限
- [ ] main.py 有执行权限
- [ ] config.yaml 权限为600（保护敏感信息）

## 🧪 功能测试

### DNS API测试
- [ ] 运行 `python main.py test-dns`
- [ ] 成功获取域名信息
- [ ] 成功获取DNS记录列表
- [ ] 成功添加TXT记录
- [ ] 成功删除TXT记录

### 证书颁发测试（测试环境）
- [ ] config.yaml中staging设为true
- [ ] 运行 `python main.py issue`
- [ ] 成功创建ACME订单
- [ ] 成功添加DNS验证记录
- [ ] Let's Encrypt验证通过
- [ ] 证书成功下载
- [ ] 证书文件保存正确

### 证书查询测试
- [ ] 运行 `python main.py info`
- [ ] 成功显示证书信息
- [ ] 运行 `python main.py list`
- [ ] 成功列出所有证书

### 证书文件检查
- [ ] certs/域名/cert.pem 存在
- [ ] certs/域名/chain.pem 存在
- [ ] certs/域名/fullchain.pem 存在
- [ ] certs/域名/privkey.pem 存在
- [ ] privkey.pem 权限为600

## 🚀 生产环境部署

### 配置调整
- [ ] config.yaml中staging设为false
- [ ] 删除测试环境生成的证书
- [ ] 运行 `python main.py issue` 获取正式证书

### Web服务器配置
- [ ] 已配置SSL证书路径
- [ ] 已重启Web服务器
- [ ] HTTPS访问正常
- [ ] 浏览器显示证书有效

### 数据库配置（如需要）
- [ ] 已配置SSL证书路径
- [ ] 已重启数据库
- [ ] SSL连接测试成功

### 自动续期设置
- [ ] 已创建续期脚本
- [ ] 已添加到crontab或systemd timer
- [ ] 已测试续期脚本运行
- [ ] 已配置服务重启命令

## 🔐 安全检查

### 文件权限
- [ ] privkey.pem 权限为600
- [ ] config.yaml 权限为600
- [ ] 证书目录不对外开放

### 敏感信息保护
- [ ] config.yaml 已添加到.gitignore
- [ ] API凭证未泄露
- [ ] 私钥未泄露

### 备份
- [ ] 已备份accounts/目录
- [ ] 已备份certs/目录
- [ ] 已设置定期备份

## 📊 监控和维护

### 日志检查
- [ ] letsencrypt.log 正常记录
- [ ] 无错误信息
- [ ] 定期清理旧日志

### 证书监控
- [ ] 已设置证书到期提醒
- [ ] 定期检查证书状态
- [ ] 确认自动续期正常工作

### 速率限制
- [ ] 了解Let's Encrypt速率限制
- [ ] 避免频繁申请证书
- [ ] 记录证书申请次数

## 📖 文档阅读

### 必读文档
- [ ] README.md - 完整使用指南
- [ ] QUICK_REFERENCE.md - 命令速查表
- [ ] PROJECT_OVERVIEW.md - 技术细节

### 推荐阅读
- [ ] examples.py - 代码示例
- [ ] Let's Encrypt速率限制文档
- [ ] DNS.LA API文档

## 🐛 故障排查准备

### 常见问题
- [ ] 知道如何查看日志
- [ ] 知道如何测试DNS API
- [ ] 知道如何验证DNS记录
- [ ] 知道如何联系支持

### 工具准备
- [ ] dig 或 nslookup 已安装
- [ ] curl 已安装
- [ ] openssl 已安装

## ✨ 最佳实践

### 开发阶段
- [ ] 始终使用测试环境（staging: true）
- [ ] 测试成功后再使用生产环境
- [ ] 保持代码和文档同步

### 生产阶段
- [ ] 定期检查证书状态
- [ ] 监控自动续期任务
- [ ] 及时更新依赖包
- [ ] 保持备份最新

### 安全实践
- [ ] 定期更改API密钥
- [ ] 使用最小权限原则
- [ ] 启用日志审计
- [ ] 定期安全审查

## 📞 支持渠道

### 项目支持
- [ ] 已阅读README.md
- [ ] 已阅读故障排查章节
- [ ] 已查看日志文件

### 外部支持
- [ ] Let's Encrypt社区论坛
- [ ] DNS.LA技术支持
- [ ] GitHub Issues（如适用）

## 🎯 下一步

完成所有检查项后：

1. **测试环境验证**
   ```bash
   python main.py test-dns
   python main.py issue  # staging: true
   python main.py info
   ```

2. **生产环境部署**
   - 修改 staging: false
   - 重新颁发证书
   - 配置Web服务器/数据库
   - 测试HTTPS访问

3. **设置自动化**
   - 配置自动续期
   - 设置监控告警
   - 备份证书文件

4. **持续维护**
   - 定期检查日志
   - 监控证书状态
   - 更新依赖包
   - 审查安全配置

---

**检查完成后，你就可以开始使用了！** 🎉

**记住：**
- ✅ 首次使用一定要用测试环境
- ✅ 保护好API凭证和私钥
- ✅ 定期备份和检查
- ✅ 遇到问题先查看日志

**祝使用顺利！** 🚀
