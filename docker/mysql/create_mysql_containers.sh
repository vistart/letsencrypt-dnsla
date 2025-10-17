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

# MySQL版本和端口映射
declare -A MYSQL_VERSIONS
MYSQL_VERSIONS[8.0]=13680
MYSQL_VERSIONS[8.4]=13684
MYSQL_VERSIONS[9.2]=13892
MYSQL_VERSIONS[latest]=13694

echo "开始创建MySQL容器..."

# 检查证书目录是否存在
if [ ! -d "$CERT_DIR" ]; then
    echo "错误: 证书目录 $CERT_DIR 不存在"
    exit 1
fi

# 检查证书文件是否存在
if [ ! -f "$CERT_DIR/cert.pem" ] || [ ! -f "$CERT_DIR/privkey.pem" ] || [ ! -f "$CERT_DIR/chain.pem" ]; then
    echo "错误: 证书文件缺失。需要 cert.pem, privkey.pem, chain.pem 在 $CERT_DIR 目录中"
    echo "当前目录内容:"
    ls -la "$CERT_DIR" || echo "无法列出目录内容"
    exit 1
fi

# 创建数据卷来存放SSL证书
echo "创建SSL证书数据卷: $VOLUME_NAME"
docker volume create $VOLUME_NAME

# 使用alpine容器复制证书到数据卷
echo "使用alpine容器复制证书到数据卷..."
docker run --rm \
  -v $VOLUME_NAME:/certs_volume \
  -v $(pwd)/$CERT_DIR:/source_certs:ro \
  registry.cn-shanghai.aliyuncs.com/vistart_public/alpine \
  sh -c "cp /source_certs/* /certs_volume/ && chmod -R 400 /certs_volume/* && ls -la /certs_volume/"

# 循环创建MySQL容器
for version in "${!MYSQL_VERSIONS[@]}"; do
    port=${MYSQL_VERSIONS[$version]}
    container_name="mysql_${version//./_}"  # 将版本号中的点替换为下划线
    
    echo "创建MySQL $version 容器，端口映射: 3306->$port"
    
    docker run -d \
      --name $container_name \
      -e MYSQL_ROOT_PASSWORD=password \
      -e MYSQL_DATABASE=test_db \
      -e TZ=Asia/Shanghai \
      -p $port:3306 \
      -v $VOLUME_NAME:/ssl_certs:ro \
      $IMAGE_BASE:$version \
      --ssl-ca=/ssl_certs/chain.pem \
      --ssl-cert=/ssl_certs/cert.pem \
      --ssl-key=/ssl_certs/privkey.pem \
      --require-secure-transport=ON
    
    echo "MySQL $version 容器已启动，名称: $container_name，端口: $port"
done

echo "所有MySQL容器创建完成！"
echo "容器列表:"
docker ps --filter "name=mysql_" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"