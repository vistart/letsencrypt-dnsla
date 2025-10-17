#!/bin/bash

# 批量移除PostgreSQL容器脚本
# 移除所有由create_postgres_containers.sh创建的PostgreSQL容器和相关资源

set -e  # 遇到错误时退出

# 定义变量
VOLUME_NAME="postgres_ssl_certs_volume"

echo "开始移除PostgreSQL容器..."

# 停止并移除PostgreSQL容器
echo "停止并移除PostgreSQL容器..."
docker stop postgres_9 postgres_10 postgres_11 postgres_12 postgres_13 postgres_14 postgres_15 postgres_16 postgres_17 postgres_latest 2>/dev/null || true
docker rm postgres_9 postgres_10 postgres_11 postgres_12 postgres_13 postgres_14 postgres_15 postgres_16 postgres_17 postgres_latest 2>/dev/null || true

# 移除数据卷
echo "移除SSL证书数据卷: $VOLUME_NAME"
docker volume rm $VOLUME_NAME 2>/dev/null || true

echo "所有PostgreSQL容器及相关资源已移除！"
echo "检查当前运行的容器:"
docker ps