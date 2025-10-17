#!/bin/bash

# 批量创建MariaDB容器脚本
# 容器名称: registry.cn-shanghai.aliyuncs.com/vistart_public/mariadb
# 标签: 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.11, 11.4, 11.7, 11.8, 12.0, latest(12.1)
# 对外端口: 从13700开始
# 证书文件目录: certs/db-dev-1-n.rho.im/

set -e  # 遇到错误时退出

# 定义变量
IMAGE_BASE="registry.cn-shanghai.aliyuncs.com/vistart_public/mariadb"
CERT_DIR="./certs/db-dev-1-n.rho.im/"
VOLUME_NAME="mariadb_ssl_certs_volume"

# MariaDB版本和端口映射 (从13702开始，跳过10.0和10.1)
MARIADB_VERSIONS=(
    "10.2:13702"
    "10.3:13703"
    "10.4:13704"
    "10.5:13705"
    "10.6:13706"
    "10.11:13707"
    "11.4:13708"
    "11.7:13709"
    "11.8:13710"
    "12.0:13711"
    "latest:13712"  # latest 对应 MariaDB 12.1
)

echo "开始创建MariaDB容器..."

# 检查证书目录是否存在
if [ ! -d "$CERT_DIR" ]; then
    echo "错误: 证书目录 $CERT_DIR 不存在"
    exit 1
fi

# 检查证书文件是否存在
if [ ! -f "$CERT_DIR/cert.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ] || [ ! -f "$CERT_DIR/chain.pem" ] || [ ! -f "$CERT_DIR/fullchain.pem" ]; then
    echo "错误: 证书文件缺失。需要 cert.pem, privkey.pem, chain.pem, fullchain.pem 在 $CERT_DIR 目录中"
    echo "当前目录内容:"
    ls -la "$CERT_DIR" || echo "无法列出目录内容"
    exit 1
fi

# 创建数据卷来存放SSL证书
echo "创建SSL证书数据卷: $VOLUME_NAME"
docker volume create $VOLUME_NAME

# 使用MariaDB容器复制证书到数据卷以确保正确的用户权限
echo "使用MariaDB容器复制证书到数据卷..."
docker run --rm \
  -v $VOLUME_NAME:/certs_volume \
  -v $(pwd)/$CERT_DIR:/source_certs:ro \
  --user root \
  $IMAGE_BASE:latest \
  sh -c "cp /source_certs/fullchain.pem /certs_volume/fullchain.pem && \
         cp /source_certs/cert.pem /certs_volume/cert.pem && \
         cp /source_certs/privkey.pem /certs_volume/privkey.pem && \
         chmod 644 /certs_volume/fullchain.pem /certs_volume/cert.pem 2>/dev/null || echo 'Warning: Could not set permissions on certificate files' && \
         chmod 600 /certs_volume/privkey.pem 2>/dev/null || echo 'Warning: Could not set permissions on private key file' && \
         chmod -R 755 /certs_volume/ 2>/dev/null || echo 'Warning: Could not set permissions on volume directory' && \
         ls -la /certs_volume/"

# 循环创建MariaDB容器
for item in "${MARIADB_VERSIONS[@]}"; do
    version=$(echo "$item" | cut -d':' -f1)
    port=$(echo "$item" | cut -d':' -f2)
    container_name="mariadb_${version//./_}"  # 将版本号中的点替换为下划线
    
    echo "创建MariaDB $version 容器，端口映射: 3306->$port"
    
    # MariaDB 10.5及更早版本不支持require_secure_transport参数
    if [[ "$version" =~ ^(10\.[0-5]|10\.1[0-1])$ ]]; then
        # 不包含 require_secure_transport 参数
        docker run -d -it \
          --name $container_name \
          -e MYSQL_ROOT_PASSWORD=password \
          -e MYSQL_DATABASE=test_db \
          -e TZ=Asia/Shanghai \
          -p $port:3306 \
          -v $VOLUME_NAME:/ssl_certs:ro \
          $IMAGE_BASE:$version \
          --ssl-ca=/ssl_certs/fullchain.pem \
          --ssl-cert=/ssl_certs/cert.pem \
          --ssl-key=/ssl_certs/privkey.pem
    else
        # 包含 require_secure_transport 参数
        docker run -d -it \
          --name $container_name \
          -e MYSQL_ROOT_PASSWORD=password \
          -e MYSQL_DATABASE=test_db \
          -e TZ=Asia/Shanghai \
          -p $port:3306 \
          -v $VOLUME_NAME:/ssl_certs:ro \
          $IMAGE_BASE:$version \
          --ssl-ca=/ssl_certs/fullchain.pem \
          --ssl-cert=/ssl_certs/cert.pem \
          --ssl-key=/ssl_certs/privkey.pem \
          --require-secure-transport=ON
    fi
    
    echo "MariaDB $version 容器已启动，名称: $container_name，端口: $port"
done

echo "所有MariaDB容器创建完成！"
echo "容器列表:"
docker ps --filter "name=mariadb_" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"