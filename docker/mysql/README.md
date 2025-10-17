# MySQL 容器管理

此目录包含用于批量管理MySQL容器的脚本。

## 功能

- 批量创建多个版本的MySQL容器
- 自动配置SSL证书以支持安全连接
- 批量移除MySQL容器及相关资源

## 要求

- Docker 已安装并运行
- 证书文件位于 `certs/db-dev-1-n.rho.im/` 目录下，包含：
  - `cert.pem` - SSL证书
  - `privkey.pem` - SSL私钥
  - `chain.pem` - 证书链

## 使用方法

### 批量创建MySQL容器

```bash
./create_mysql_containers.sh
```

此脚本将：

1. 检查证书文件是否存在
2. 创建名为 `mysql_ssl_certs_volume` 的Docker数据卷
3. 使用 `registry.cn-shanghai.aliyuncs.com/vistart_public/alpine` 容器将证书复制到数据卷
4. 创建以下MySQL容器：
   - MySQL 8.0，端口映射 3306->13680
   - MySQL 8.4，端口映射 3306->13684
   - MySQL 9.2，端口映射 3306->13892
   - MySQL latest，端口映射 3306->13694

所有容器都使用以下环境变量：
- `MYSQL_ROOT_PASSWORD=password`
- `MYSQL_DATABASE=test_db`
- `TZ=Asia/Shanghai`

### 批量移除MySQL容器

```bash
./remove_mysql_containers.sh
```

此脚本将：
1. 停止并移除所有MySQL容器
2. 删除SSL证书数据卷

## 容器配置

每个MySQL容器都配置了SSL支持：
- SSL证书来自数据卷，路径为 `/ssl_certs/`
- 启用了 `require_secure_transport=ON`，强制使用安全连接
- 默认数据库为 `test_db`

## 端口映射

- 13680: MySQL 8.0
- 13684: MySQL 8.4
- 13892: MySQL 9.2
- 13694: MySQL latest