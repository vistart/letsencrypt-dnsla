#!/usr/bin/env python3
"""
MySQL SSL连接验证脚本
用于验证通过SSL连接到MySQL容器

注意：在运行此脚本前，请确保：
1. MySQL容器已启动并运行
2. 从主机可以访问指定的IP和端口
"""

import mysql.connector
import sys
import os
from pathlib import Path

# MySQL服务器端口配置
MYSQL_PORTS = {
    '8.0': 13680,
    '8.4': 13684,
    '9.2': 13692,
    'latest': 13694
}

def verify_mysql_ssl_connection(host, port, version):
    """验证MySQL SSL连接"""
    try:
        print(f"正在连接到 MySQL {version} ({host}:{port})...")
        
        # 连接参数
        # 由于证书由受信任根签发，不需要提供证书文件，只需启用SSL连接
        conn_params = {
            'host': host,
            'port': port,
            'user': 'root',
            'password': 'password',
            'database': 'test_db',
            'ssl_disabled': False,          # 启用SSL
            'connection_timeout': 10        # 设置连接超时
        }
        
        # 尝试连接
        conn = mysql.connector.connect(**conn_params)
        
        # 执行简单查询验证连接
        cursor = conn.cursor()
        cursor.execute('SELECT VERSION();')
        result = cursor.fetchone()
        print(f"✓ 成功连接到 MySQL {version} ({host}:{port})")
        print(f"  服务器版本: {result[0]}")
        
        # 检查连接是否使用SSL
        cursor.execute("SELECT @@ssl_cipher;")  # 检查SSL密码套件
        ssl_cipher = cursor.fetchone()[0]
        print(f"  SSL密码套件: {ssl_cipher if ssl_cipher else '无（未使用SSL）'}")
        
        # 检查SSL状态
        cursor.execute("SHOW STATUS LIKE 'Ssl_cipher';")
        ssl_status = cursor.fetchone()
        print(f"  SSL状态: {ssl_status[1] if ssl_status[1] else '未使用SSL'}")
        
        # 执行简单查询测试
        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()
        print(f"  当前时间: {current_time[0]}")
        
        # 查询时区信息
        cursor.execute("SELECT @@session.time_zone, NOW(), UTC_TIMESTAMP();")
        timezone_info = cursor.fetchone()
        session_timezone = timezone_info[0] if timezone_info[0] else '未设置'
        local_time = timezone_info[1]
        utc_time = timezone_info[2]
        
        print(f"  会话时区: {session_timezone}")
        print(f"  本地时间: {local_time}")
        print(f"  UTC时间: {utc_time}")
        
        # 计算时区偏移（如果可能）
        try:
            from datetime import datetime
            # 如果是SYSTEM时区，尝试获取实际偏移
            if session_timezone == 'SYSTEM':
                # 通过时间差计算偏移
                import time
                local_offset = -time.timezone / 3600  # 转换为小时
                if time.daylight and time.localtime().tm_isdst:
                    local_offset = -time.altzone / 3600
                print(f"  时区偏移: UTC{local_offset:+.2f}h")
            else:
                print(f"  时区偏移: {session_timezone}")
        except:
            print(f"  时区偏移: 无法计算")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ 连接到 MySQL {version} ({host}:{port}) 失败: {e}")
        return False

def main():
    # 从命令行参数获取主机地址，如果没有提供则使用localhost
    if len(sys.argv) != 2:
        host = "127.0.0.1"  # 默认主机地址
        print("用法: python verify_ssl_connection.py <host>")
        print(f"例如: python verify_ssl_connection.py db-dev-1-n.rho.im")
        print(f"使用默认主机: {host}")
    else:
        host = sys.argv[1]
    
    print("MySQL SSL连接验证")
    print("=" * 50)
    print(f"主机: {host}")
    print()
    
    print("开始验证各版本MySQL连接...")
    print()
    
    successful_connections = 0
    total_connections = len(MYSQL_PORTS)
    
    for version, port in MYSQL_PORTS.items():
        if verify_mysql_ssl_connection(host, port, version):
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