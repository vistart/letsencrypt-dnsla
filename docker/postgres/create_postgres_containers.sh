#!/bin/bash

# 批量创建PostgreSQL容器脚本
# 容器名称: registry.cn-shanghai.aliyuncs.com/vistart_public/postgres
# 标签: 9, 10, 11, 12, 13, 14, 15, 16, 17, latest(18)
# 对外端口: 15432, 15433, 15434, 15435, 15436, 15437, 15438, 15439, 15440, 15441
# 证书文件目录: certs/db-dev-1-n.rho.im/

set -e  # 遇到错误时退出

# 定义变量
IMAGE_BASE="registry.cn-shanghai.aliyuncs.com/vistart_public/postgres"
CERT_DIR="./certs/db-dev-1-n.rho.im/"
VOLUME_NAME="postgres_ssl_certs_volume"

# PostgreSQL版本和端口映射 (从15432开始，对应标准PostgreSQL端口5432)
declare -A POSTGRES_VERSIONS
POSTGRES_VERSIONS[9]=15432
POSTGRES_VERSIONS[10]=15433
POSTGRES_VERSIONS[11]=15434
POSTGRES_VERSIONS[12]=15435
POSTGRES_VERSIONS[13]=15436
POSTGRES_VERSIONS[14]=15437
POSTGRES_VERSIONS[15]=15438
POSTGRES_VERSIONS[16]=15439
POSTGRES_VERSIONS[17]=15440
POSTGRES_VERSIONS[latest]=15441  # latest 对应 PostgreSQL 18

echo "开始创建PostgreSQL容器..."

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
  sh -c "cp /source_certs/cert.pem /certs_volume/server.crt && \
         cp /source_certs/privkey.pem /certs_volume/server.key && \
         cp /source_certs/chain.pem /certs_volume/root.crt && \
         chmod 600 /certs_volume/server.key && \
         chmod 644 /certs_volume/server.crt && \
         chmod 644 /certs_volume/root.crt && \
         ls -la /certs_volume/"

# 循环创建PostgreSQL容器
for version in "${!POSTGRES_VERSIONS[@]}"; do
    port=${POSTGRES_VERSIONS[$version]}
    container_name="postgres_${version//./_}"  # 将版本号中的点替换为下划线（虽然PostgreSQL版本号都是整数）
    
    echo "创建PostgreSQL $version 容器，端口映射: 5432->$port"
    
    # 设置环境变量
    docker run -d \
      --name $container_name \
      -e POSTGRES_PASSWORD=password \
      -e POSTGRES_DB=test_db \
      -e TZ=Asia/Shanghai \
      -p $port:5432 \
      -v $VOLUME_NAME:/var/lib/postgresql/certs:ro \
      $IMAGE_BASE:$version \
      -c ssl=on \
      -c ssl_cert_file=/var/lib/postgresql/certs/server.crt \
      -c ssl_key_file=/var/lib/postgresql/certs/server.key \
      -c ssl_ca_file=/var/lib/postgresql/certs/root.crt
    
    echo "PostgreSQL $version 容器已启动，名称: $container_name，端口: $port"
done

echo "所有PostgreSQL容器创建完成！"
echo "容器列表:"
docker ps --filter "name=postgres_" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"