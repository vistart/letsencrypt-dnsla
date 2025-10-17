# PostgreSQL 容器管理

此目录包含用于批量管理PostgreSQL容器的脚本。

## 功能

- 批量创建多个版本的PostgreSQL容器
- 自动配置SSL证书以支持安全连接
- 批量移除PostgreSQL容器及相关资源

## 要求

- Docker 已安装并运行
- 证书文件位于 `certs/db-dev-1-n.rho.im/` 目录下，包含：
  - `cert.pem` - SSL证书
  - `privkey.pem` - SSL私钥
  - `chain.pem` - 证书链

## 使用方法

### 批量创建PostgreSQL容器

```bash
./create_postgres_containers.sh
```

此脚本将：

1. 检查证书文件是否存在
2. 创建名为 `postgres_ssl_certs_volume` 的Docker数据卷
3. 使用 `registry.cn-shanghai.aliyuncs.com/vistart_public/alpine` 容器将证书复制到数据卷，并按PostgreSQL要求重命名：
   - `cert.pem` -> `server.crt`
   - `privkey.pem` -> `server.key`
   - `chain.pem` -> `root.crt`
4. 创建以下PostgreSQL容器：
   - PostgreSQL 9，端口映射 5432->15432
   - PostgreSQL 10，端口映射 5432->15433
   - PostgreSQL 11，端口映射 5432->15434
   - PostgreSQL 12，端口映射 5432->15435
   - PostgreSQL 13，端口映射 5432->15436
   - PostgreSQL 14，端口映射 5432->15437
   - PostgreSQL 15，端口映射 5432->15438
   - PostgreSQL 16，端口映射 5432->15439
   - PostgreSQL 17，端口映射 5432->15440
   - PostgreSQL latest (18)，端口映射 5432->15441

所有容器都使用以下环境变量：
- `POSTGRES_PASSWORD=password`
- `POSTGRES_DB=test_db`
- `TZ=Asia/Shanghai`

### 批量移除PostgreSQL容器

```bash
./remove_postgres_containers.sh
```

此脚本将：
1. 停止并移除所有PostgreSQL容器
2. 删除SSL证书数据卷

## 容器配置

每个PostgreSQL容器都配置了SSL支持：
- SSL证书来自数据卷，路径为 `/var/lib/postgresql/certs/`
- 通过命令行参数启用SSL：
  - `-c ssl=on`
  - `-c ssl_cert_file=/var/lib/postgresql/certs/server.crt`
  - `-c ssl_key_file=/var/lib/postgresql/certs/server.key`
  - `-c ssl_ca_file=/var/lib/postgresql/certs/root.crt`

## 端口映射

- 15432: PostgreSQL 9
- 15433: PostgreSQL 10
- 15434: PostgreSQL 11
- 15435: PostgreSQL 12
- 15436: PostgreSQL 13
- 15437: PostgreSQL 14
- 15438: PostgreSQL 15
- 15439: PostgreSQL 16
- 15440: PostgreSQL 17
- 15441: PostgreSQL latest (18)