#!/usr/bin/env python3
"""
PostgreSQL SSL连接验证脚本
用于验证通过SSL连接到PostgreSQL容器

注意：在运行此脚本前，请确保：
1. PostgreSQL容器已启动并运行
2. 从主机可以访问指定的IP和端口
"""

import psycopg
import ssl
import sys
import os
from pathlib import Path

# PostgreSQL服务器端口配置
PG_PORTS = {
    9: 15432,
    10: 15433,
    11: 15434,
    12: 15435,
    13: 15436,
    14: 15437,
    15: 15438,
    16: 15439,
    17: 15440,
    'latest': 15441  # 对应PostgreSQL 18
}

def verify_postgres_ssl_connection(host, port, version):
    """验证PostgreSQL SSL连接"""
    try:
        print(f"正在连接到 PostgreSQL {version} ({host}:{port})...")
        
        # 连接参数
        # 由于证书由受信任根签发，不需要提供证书文件，只需启用SSL连接
        conn_params = {
            'host': host,
            'port': port,
            'user': 'root',
            'password': 'password',
            'dbname': 'test_db',
            'sslmode': 'require',    # 只需要SSL连接，不需要验证证书
        }
        
        # 尝试连接
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # 执行简单查询验证连接
                cur.execute('SELECT version();')
                result = cur.fetchone()
                print(f"✓ 成功连接到 PostgreSQL {version} ({host}:{port})")
                print(f"  服务器版本: {result[0][:50]}...")
                
                # 检查连接是否使用SSL (PostgreSQL使用不同的函数)
                cur.execute("SELECT count(*) > 0 FROM pg_stat_ssl WHERE ssl = true AND pid = pg_backend_pid();")
                ssl_query_result = cur.fetchone()
                if ssl_query_result:
                    ssl_used = ssl_query_result[0] or False
                    print(f"  SSL连接状态: {'是' if ssl_used else '否'}")
                else:
                    # 如果查询失败，尝试另一种方法
                    try:
                        cur.execute("SELECT ssl, count(*) FROM pg_stat_ssl GROUP BY ssl;")
                        ssl_status = cur.fetchall()
                        ssl_used = any(row[0] for row in ssl_status)
                        print(f"  SSL连接状态: {'是' if ssl_used else '否'}")
                    except:
                        print("  SSL连接状态: 无法确定")
                
        return True
        
    except Exception as e:
        print(f"✗ 连接到 PostgreSQL {version} ({host}:{port}) 失败: {e}")
        return False

def main():
    # 从命令行参数获取主机地址，如果没有提供则使用默认值
    if len(sys.argv) != 2:
        host = "127.0.0.1"  # 默认主机地址
        print("用法: python verify_ssl_connection.py <host>")
        print(f"例如: python verify_ssl_connection.py db-dev-1-n.rho.im")
        print(f"使用默认主机: {host}")
    else:
        host = sys.argv[1]
    
    print("PostgreSQL SSL连接验证")
    print("=" * 50)
    print(f"主机: {host}")
    print()
    
    print("开始验证各版本PostgreSQL连接...")
    print()
    
    successful_connections = 0
    total_connections = len(PG_PORTS)
    
    for version, port in PG_PORTS.items():
        if verify_postgres_ssl_connection(host, port, version):
            successful_connections += 1
        print()
    
    print("=" * 50)
    print(f"验证完成: {successful_connections}/{total_connections} 个连接成功")
    
    if successful_connections > 0:
        print("SSL连接验证成功！")
        return True
    else:
        print("所有SSL连接验证失败！")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)