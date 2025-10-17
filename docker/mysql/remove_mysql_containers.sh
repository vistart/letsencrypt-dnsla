#!/bin/bash

# 批量移除MySQL容器脚本
# 移除所有由create_mysql_containers.sh创建的MySQL容器和相关资源

set -e  # 遇到错误时退出

# 定义变量
VOLUME_NAME="mysql_ssl_certs_volume"

echo "开始移除MySQL容器..."

# 停止并移除MySQL容器
echo "停止并移除MySQL容器..."
docker stop mysql_8_0 mysql_8_4 mysql_9_2 mysql_latest 2>/dev/null || true
docker rm mysql_8_0 mysql_8_4 mysql_9_2 mysql_latest 2>/dev/null || true

# 移除数据卷
echo "移除SSL证书数据卷: $VOLUME_NAME"
docker volume rm $VOLUME_NAME 2>/dev/null || true

# 清理相关镜像（可选，如果需要）
# docker rmi registry.cn-shanghai.aliyuncs.com/vistart_public/mysql:8.0 2>/dev/null || true
# docker rmi registry.cn-shanghai.aliyuncs.com/vistart_public/mysql:8.4 2>/dev/null || true
# docker rmi registry.cn-shanghai.aliyuncs.com/vistart_public/mysql:9.2 2>/dev/null || true
# docker rmi registry.cn-shanghai.aliyuncs.com/vistart_public/mysql:latest 2>/dev/null || true

echo "所有MySQL容器及相关资源已移除！"
echo "检查当前运行的容器:"
docker ps