#!/bin/bash

# 批量移除MariaDB容器脚本
# 移除所有由create_mariadb_containers.sh创建的MariaDB容器和相关资源

set -e  # 遇到错误时退出

# 定义变量
VOLUME_NAME="mariadb_ssl_certs_volume"

echo "开始移除MariaDB容器..."

# 停止并移除MariaDB容器
echo "停止并移除MariaDB容器..."
docker stop mariadb_10_0 mariadb_10_1 mariadb_10_2 mariadb_10_3 mariadb_10_4 mariadb_10_5 mariadb_10_6 mariadb_10_11 mariadb_11_4 mariadb_11_7 mariadb_11_8 mariadb_12_0 mariadb_latest 2>/dev/null || true
docker rm mariadb_10_0 mariadb_10_1 mariadb_10_2 mariadb_10_3 mariadb_10_4 mariadb_10_5 mariadb_10_6 mariadb_10_11 mariadb_11_4 mariadb_11_7 mariadb_11_8 mariadb_12_0 mariadb_latest 2>/dev/null || true

# 移除数据卷
echo "移除SSL证书数据卷: $VOLUME_NAME"
docker volume rm $VOLUME_NAME 2>/dev/null || true

echo "所有MariaDB容器及相关资源已移除！"
echo "检查当前运行的容器:"
docker ps