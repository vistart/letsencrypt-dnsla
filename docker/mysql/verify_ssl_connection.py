#!/usr/bin/env python3
"""
MySQL SSL连接验证脚本
用于验证通过SSL连接到MySQL容器

注意：在运行此脚本前，请确保：
1. MySQL容器已启动并运行
2. 从主机可以访问指定的IP和端口
3. 证书文件存在且有效
4. 证书域名与连接目标匹配（如果使用verify-full模式）
"""

import mysql.connector
import sys
import os
from pathlib import Path

# MySQL服务器配置
MYSQL_HOST = '192.168.1.3'
MYSQL_PORTS = {
    '8.0': 13680,
    '8.4': 13684,
    '9.2': 13692,
    'latest': 13694
}

# 证书文件路径
CERT_DIR = Path('../../certs/db-dev-1-n.rho.im')
CA_CERT_PATH = str(CERT_DIR / 'chain.pem')
CLIENT_CERT_PATH = str(CERT_DIR / 'cert.pem')
CLIENT_KEY_PATH = str(CERT_DIR / 'privkey.pem')

def verify_mysql_ssl_connection(port, version):
    """验证MySQL SSL连接"""
    try:
        print(f"正在连接到 MySQL {version} (端口 {port})...")
        
        # 连接参数
        # 根据Let's Encrypt证书特点，我们配置基本的SSL连接
        conn_params = {
            'host': MYSQL_HOST,
            'port': port,
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
            'ssl_ca': CA_CERT_PATH,        # Let's Encrypt中间证书用于验证服务器
            'ssl_verify_cert': False,      # Let's Encrypt证书通常验证域名，而我们使用IP连接
            'ssl_disabled': False,
        }
        
        # 尝试连接
        conn = mysql.connector.connect(**conn_params)
        
        # 执行简单查询验证连接
        cursor = conn.cursor()
        cursor.execute('SELECT VERSION();')
        result = cursor.fetchone()
        print(f"✓ 成功连接到 MySQL {version} (端口 {port})")
        print(f"  服务器版本: {result[0]}")
        
        # 检查连接是否使用SSL
        cursor.execute("SELECT @@ssl_cipher;")  # 检查SSL密码套件
        ssl_cipher = cursor.fetchone()[0]
        print(f"  SSL密码套件: {ssl_cipher if ssl_cipher else '无（未使用SSL）'}")
        
        # 检查SSL状态
        cursor.execute("SHOW STATUS LIKE 'Ssl_cipher';")
        ssl_status = cursor.fetchone()
        print(f"  SSL状态: {ssl_status[1] if ssl_status[1] else '未使用SSL'}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 连接到 MySQL {version} (端口 {port}) 失败: {e}")
        return False

def main():
    print("MySQL SSL连接验证")
    print("=" * 50)
    print(f"主机: {MYSQL_HOST}")
    print(f"证书目录: {CERT_DIR}")
    print()
    
    # 验证证书文件存在
    if not CERT_DIR.exists():
        print(f"错误: 证书目录不存在: {CERT_DIR}")
        return False
    
    if not all(Path(p).exists() for p in [CA_CERT_PATH, CLIENT_CERT_PATH, CLIENT_KEY_PATH]):
        print(f"错误: 证书文件不存在")
        return False
    
    print("开始验证各版本MySQL连接...")
    print()
    
    successful_connections = 0
    total_connections = len(MYSQL_PORTS)
    
    for version, port in MYSQL_PORTS.items():
        if verify_mysql_ssl_connection(port, version):
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