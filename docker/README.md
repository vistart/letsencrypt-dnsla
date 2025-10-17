# 数据库容器管理

此目录包含多个子目录，每个子目录对应一种数据库的容器管理脚本。

## 支持的数据库

- [MySQL](./mysql/README.md) - 包含MySQL 8.0, 8.4, 9.2, latest版本的容器管理脚本
- [PostgreSQL](./postgres/README.md) - 包含PostgreSQL 9, 10, 11, 12, 13, 14, 15, 16, 17, latest版本的容器管理脚本
- [MariaDB](./mariadb/README.md) - 包含MariaDB 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.11, 11.4, 11.7, 11.8, 12.0, latest版本的容器管理脚本

## 通用特性

- 所有脚本都与旧版本bash兼容
- 统一的SSL证书管理方案
- 自动化证书权限设置
- 安全的数据库连接配置

## 证书管理

所有数据库容器都配置了SSL证书支持，证书文件来自 `certs/db-dev-1-n.rho.im/` 目录，包含：
- `fullchain.pem` - 完整证书链（服务器证书+中间证书）
- `cert.pem` - 服务器证书（仅当前域名证书）
- `privkey.pem` - SSL私钥
- `chain.pem` - 证书链（中间证书）

数据库配置：
- MySQL/MariaDB: 使用 fullchain.pem 作为服务器证书，chain.pem 作为CA证书
- PostgreSQL: 使用 fullchain.pem 作为服务器证书，chain.pem 作为CA证书

## 使用方法

进入对应数据库的子目录，按照各子目录的README.md文件说明使用脚本。

## 经验总结

在使用这些脚本时，请注意：

1. **权限管理** - 使用相应的数据库容器作为跳板来设置证书权限，确保容器内部进程可以访问证书文件
2. **版本兼容性** - 某些旧版本的数据库不支持某些安全参数（如MariaDB 10.5及更早版本不支持require_secure_transport）
3. **安全连接** - 所有数据库容器都配置为要求SSL连接，客户端连接时需使用相应的SSL参数
4. **权限错误处理** - 脚本现在包含对chmod命令失败的处理，以适应不同的文件系统环境
5. **PostgreSQL特殊权限** - PostgreSQL容器需要私钥文件具有正确的权限(600)且由PostgreSQL用户(UID 999)拥有，否则会出现"Permission denied"错误