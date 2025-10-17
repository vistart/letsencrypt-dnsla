#!/bin/bash

# 批量创建MySQL容器脚本
# 容器名称: registry.cn-shanghai.aliyuncs.com/vistart_public/mysql
# 标签: 8.0, 8.4, 9.2, latest
# 对外端口: 13680, 13684, 13892, 13694
# 证书文件目录: certs/db-dev-1-n.rho.im/

set -e  # 遇到错误时退出

# 定义变量
IMAGE_BASE="registry.cn-shanghai.aliyuncs.com/vistart_public/mysql"
CERT_DIR="./certs/db-dev-1-n.rho.im/"
VOLUME_NAME="mysql_ssl_certs_volume"

# MySQL版本和端口映射 (使用普通数组替代关联数组以提高bash兼容性)
MYSQL_VERSIONS=(
    "8.0:13680"
    "8.4:13684"
    "9.2:13692"
    "latest:13694"
)

echo "开始创建MySQL容器..."

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

# 使用MySQL容器复制证书到数据卷以确保正确的用户权限
echo "使用MySQL容器复制证书到数据卷..."
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

# 循环创建MySQL容器
for item in "${MYSQL_VERSIONS[@]}"; do
    version=$(echo "$item" | cut -d':' -f1)
    port=$(echo "$item" | cut -d':' -f2)
    container_name="mysql_${version//./_}"  # 将版本号中的点替换为下划线
    
    echo "创建MySQL $version 容器，端口映射: 3306->$port"
    
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
    
    echo "MySQL $version 容器已启动，名称: $container_name，端口: $port"
done

echo "所有MySQL容器创建完成！"
echo "容器列表:"
docker ps --filter "name=mysql_" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"