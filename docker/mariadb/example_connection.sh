#!/bin/bash

# MariaDB容器连接示例

echo "MariaDB容器信息："
echo "1. MariaDB 10.2: localhost:13702"
echo "2. MariaDB 10.3: localhost:13703"
echo "3. MariaDB 10.4: localhost:13704"
echo "4. MariaDB 10.5: localhost:13705"
echo "5. MariaDB 10.6: localhost:13706"
echo "6. MariaDB 10.11: localhost:13707"
echo "7. MariaDB 11.4: localhost:13708"
echo "8. MariaDB 11.7: localhost:13709"
echo "9. MariaDB 11.8: localhost:13710"
echo "10. MariaDB 12.0: localhost:13711"
echo "11. MariaDB latest(12.1): localhost:13712"
echo ""
echo "连接示例（使用SSL）："
echo "mysql --host=127.0.0.1 --port=13700 --user=root --password=password --ssl-mode=REQUIRED test_db"
echo ""
echo "或者使用mysql命令行客户端："
echo "mysql -h 127.0.0.1 -P 13700 -u root -p" 
echo ""
echo "注意：由于容器配置了 require_secure_transport=ON（对10.6+版本），必须使用SSL连接"