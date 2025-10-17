# MariaDB 容器管理

此目录包含用于批量管理MariaDB容器的脚本。

## 功能

- 批量创建多个版本的MariaDB容器
- 自动配置SSL证书以支持安全连接
- 批量移除MariaDB容器及相关资源

## 要求

- Docker 已安装并运行
- 证书文件位于 `certs/db-dev-1-n.rho.im/` 目录下，包含：
  - `cert.pem` - SSL证书
  - `privkey.pem` - SSL私钥
  - `chain.pem` - 证书链

## 使用方法

### 批量创建MariaDB容器

```bash
./create_mariadb_containers.sh
```

此脚本将：

1. 检查证书文件是否存在
2. 创建名为 `mariadb_ssl_certs_volume` 的Docker数据卷
3. 使用 `registry.cn-shanghai.aliyuncs.com/vistart_public/alpine` 容器将证书复制到数据卷
4. 创建以下MariaDB容器：
   - MariaDB 10.0，端口映射 3306->13700
   - MariaDB 10.1，端口映射 3306->13701
   - MariaDB 10.2，端口映射 3306->13702
   - MariaDB 10.3，端口映射 3306->13703
   - MariaDB 10.4，端口映射 3306->13704
   - MariaDB 10.5，端口映射 3306->13705
   - MariaDB 10.6，端口映射 3306->13706
   - MariaDB 10.11，端口映射 3306->13707
   - MariaDB 11.4，端口映射 3306->13708
   - MariaDB 11.7，端口映射 3306->13709
   - MariaDB 11.8，端口映射 3306->13710
   - MariaDB 12.0，端口映射 3306->13711
   - MariaDB latest (12.1)，端口映射 3306->13712

所有容器都使用以下环境变量：
- `MYSQL_ROOT_PASSWORD=password`
- `MYSQL_DATABASE=test_db`
- `TZ=Asia/Shanghai`

### 批量移除MariaDB容器

```bash
./remove_mariadb_containers.sh
```

此脚本将：
1. 停止并移除所有MariaDB容器
2. 删除SSL证书数据卷

## 容器配置

每个MariaDB容器都配置了SSL支持：
- SSL证书来自数据卷，路径为 `/ssl_certs/`
- 启用了 `require_secure_transport=ON`，强制使用安全连接
- 默认数据库为 `test_db`

## 端口映射

- 13700: MariaDB 10.0
- 13701: MariaDB 10.1
- 13702: MariaDB 10.2
- 13703: MariaDB 10.3
- 13704: MariaDB 10.4
- 13705: MariaDB 10.5
- 13706: MariaDB 10.6
- 13707: MariaDB 10.11
- 13708: MariaDB 11.4
- 13709: MariaDB 11.7
- 13710: MariaDB 11.8
- 13711: MariaDB 12.0
- 13712: MariaDB latest (12.1)