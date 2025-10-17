#!/bin/bash

# PostgreSQL容器连接示例

echo "PostgreSQL容器信息："
echo "1. PostgreSQL 9: localhost:15432"
echo "2. PostgreSQL 10: localhost:15433" 
echo "3. PostgreSQL 11: localhost:15434"
echo "4. PostgreSQL 12: localhost:15435"
echo "5. PostgreSQL 13: localhost:15436"
echo "6. PostgreSQL 14: localhost:15437"
echo "7. PostgreSQL 15: localhost:15438"
echo "8. PostgreSQL 16: localhost:15439"
echo "9. PostgreSQL 17: localhost:15440"
echo "10. PostgreSQL latest(18): localhost:15441"
echo ""
echo "连接示例（使用SSL）："
echo "psql -h 127.0.0.1 -p 15432 -U postgres -d test_db -W"
echo ""
echo "使用环境变量连接："
echo "PGHOST=127.0.0.1 PGPORT=15432 PGUSER=postgres PGPASSWORD=password PGDATABASE=test_db psql"
echo ""
echo "注意：由于容器配置了SSL，连接时可能需要指定SSL模式"