#!/bin/bash

# MySQL容器连接示例

echo "MySQL容器信息："
echo "1. MySQL 8.0: localhost:13680"
echo "2. MySQL 8.4: localhost:13684" 
echo "3. MySQL 9.2: localhost:13692"
echo "4. MySQL latest: localhost:13694"
echo ""
echo "连接示例（使用SSL）："
echo "mysql --host=127.0.0.1 --port=13680 --user=root --password=password --ssl-mode=REQUIRED test_db"
echo ""
echo "或者使用mysql命令行客户端："
echo "mysql -h 127.0.0.1 -P 13680 -u root -p" 
echo ""
echo "注意：由于容器配置了 require_secure_transport=ON，必须使用SSL连接"