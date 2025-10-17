#!/usr/bin/env python3
"""
PostgreSQL SSL连接验证脚本
用于验证通过SSL连接到PostgreSQL容器

注意：在运行此脚本前，请确保：
1. PostgreSQL容器已启动并运行
2. 从主机可以访问指定的IP和端口
3. 证书文件存在且有效
4. 证书域名与连接目标匹配（如果使用verify-full模式）
"""

import psycopg
import ssl
import sys
import os
from pathlib import Path

# PostgreSQL服务器配置
PG_HOST = '192.168.1.3'
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

# 证书文件路径
# 请注意：在创建容器时，证书文件被复制到数据卷并重命名为
# server.crt (来自 fullchain.pem), server.key (来自 privkey.pem), root.crt (来自 chain.pem)
# 这些文件位于数据卷中，客户端连接需要从本地获取原始证书文件
CERT_DIR = Path('../../certs/db-dev-1-n.rho.im')
CA_CERT_PATH = str(CERT_DIR / 'chain.pem')
CLIENT_CERT_PATH = str(CERT_DIR / 'cert.pem')
CLIENT_KEY_PATH = str(CERT_DIR / 'privkey.pem')

def verify_postgres_ssl_connection(port, version):
    """验证PostgreSQL SSL连接"""
    try:
        print(f"正在连接到 PostgreSQL {version} (端口 {port})...")
        
        # 连接参数
        # 根据Let's Encrypt证书特点，使用require模式进行SSL连接
        # 由于我们使用IP而非域名连接，避免使用verify-full模式
        conn_params = {
            'host': PG_HOST,
            'port': port,
            'user': 'postgres',
            'password': 'password',
            'dbname': 'test_db',
            'sslmode': 'require',      # 只要求SSL连接，不验证证书
            'sslrootcert': CA_CERT_PATH,    # CA证书路径
        }
        
        # 尝试连接
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # 执行简单查询验证连接
                cur.execute('SELECT version();')
                result = cur.fetchone()
                print(f"✓ 成功连接到 PostgreSQL {version} (端口 {port})")
                print(f"  服务器版本: {result[0][:50]}...")
                
                # 检查连接是否使用SSL
                cur.execute("SELECT ssl_is_used();")
                ssl_used = cur.fetchone()[0]
                print(f"  SSL连接状态: {'是' if ssl_used else '否'}")
                
        return True
        
    except Exception as e:
        print(f"✗ 连接到 PostgreSQL {version} (端口 {port}) 失败: {e}")
        return False

def main():
    print("PostgreSQL SSL连接验证")
    print("=" * 50)
    print(f"主机: {PG_HOST}")
    print(f"证书目录: {CERT_DIR}")
    print()
    
    # 验证证书文件存在
    if not CERT_DIR.exists():
        print(f"错误: 证书目录不存在: {CERT_DIR}")
        return False
    
    if not all(Path(p).exists() for p in [CA_CERT_PATH, CLIENT_CERT_PATH, CLIENT_KEY_PATH]):
        print(f"错误: 证书文件不存在")
        return False
    
    print("开始验证各版本PostgreSQL连接...")
    print()
    
    successful_connections = 0
    total_connections = len(PG_PORTS)
    
    for version, port in PG_PORTS.items():
        if verify_postgres_ssl_connection(port, version):
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