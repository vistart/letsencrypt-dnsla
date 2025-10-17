#!/usr/bin/env python3
"""
DNS.LA API 客户端
用于管理DNS记录以完成ACME DNS-01验证
"""

import base64
import json
import logging
import time
from typing import Dict, List, Optional

import requests


logger = logging.getLogger(__name__)


class DNSLAClient:
    """DNS.LA API客户端"""
    
    # 记录类型映射
    RECORD_TYPES = {
        'A': 1,
        'NS': 2,
        'CNAME': 5,
        'MX': 15,
        'TXT': 16,
        'AAAA': 28,
        'SRV': 33,
        'CAA': 257,
        'URL': 256,
    }
    
    def __init__(self, api_id: str, api_secret: str, base_url: str = "https://api.dns.la"):
        """
        初始化DNS.LA客户端
        
        Args:
            api_id: API ID（用户名）
            api_secret: API Secret（密码）
            base_url: API基础URL
        """
        self.api_id = api_id
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # 计算Basic Auth token
        self.auth_token = self._calculate_auth_token()
        self.session.headers.update({
            'Authorization': f'Basic {self.auth_token}',
            'Content-Type': 'application/json; charset=utf-8',
        })
        
        logger.info("DNS.LA客户端初始化成功")
    
    def _calculate_auth_token(self) -> str:
        """
        计算Basic Auth token
        
        Returns:
            Base64编码的认证token
        """
        credentials = f"{self.api_id}:{self.api_secret}"
        token = base64.b64encode(credentials.encode()).decode()
        logger.debug(f"计算得到的Auth Token: {token}")
        return token
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发送API请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            API响应数据
            
        Raises:
            Exception: API请求失败时抛出异常
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 200:
                error_msg = data.get('msg', 'Unknown error')
                raise Exception(f"API错误: {error_msg} (code: {data.get('code')})")
            
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise
    
    def get_domain_info(self, domain: str) -> Optional[Dict]:
        """
        获取域名信息
        
        Args:
            domain: 域名
            
        Returns:
            域名信息字典，如果域名不存在返回None
        """
        try:
            response = self._request('GET', f'/api/domain', params={'domain': domain})
            return response.get('data')
        except Exception as e:
            logger.error(f"获取域名信息失败: {e}")
            return None
    
    def get_record_list(
        self,
        domain_id: str,
        page_index: int = 1,
        page_size: int = 100,
        record_type: Optional[str] = None,
        host: Optional[str] = None,
        data: Optional[str] = None,
    ) -> List[Dict]:
        """
        获取DNS记录列表
        
        Args:
            domain_id: 域名ID
            page_index: 页码
            page_size: 每页记录数
            record_type: 记录类型（如'TXT'）
            host: 主机头
            data: 记录值
            
        Returns:
            DNS记录列表
        """
        params = {
            'pageIndex': page_index,
            'pageSize': page_size,
            'domainId': domain_id,
        }
        
        if record_type:
            params['type'] = self.RECORD_TYPES.get(record_type.upper())
        if host is not None:
            params['host'] = host
        if data is not None:
            params['data'] = data
        
        try:
            response = self._request('GET', '/api/recordList', params=params)
            records = response.get('data', {}).get('results', [])
            logger.info(f"获取到 {len(records)} 条DNS记录")
            return records
        except Exception as e:
            logger.error(f"获取DNS记录列表失败: {e}")
            return []
    
    def add_record(
        self,
        domain_id: str,
        record_type: str,
        host: str,
        data: str,
        ttl: int = 600,
        **kwargs
    ) -> Optional[str]:
        """
        添加DNS记录
        
        Args:
            domain_id: 域名ID
            record_type: 记录类型（如'TXT'）
            host: 主机头
            data: 记录值
            ttl: TTL值
            **kwargs: 其他参数（groupId, lineId, preference, weight, dominant）
            
        Returns:
            新记录的ID，失败返回None
        """
        payload = {
            'domainId': domain_id,
            'type': self.RECORD_TYPES.get(record_type.upper()),
            'host': host,
            'data': data,
            'ttl': ttl,
        }
        
        # 添加可选参数
        for key in ['groupId', 'lineId', 'preference', 'weight', 'dominant']:
            if key in kwargs:
                payload[key] = kwargs[key]
        
        try:
            response = self._request('POST', '/api/record', json=payload)
            record_id = response.get('data', {}).get('id')
            logger.info(f"成功添加DNS记录: {host} -> {data} (ID: {record_id})")
            return record_id
        except Exception as e:
            logger.error(f"添加DNS记录失败: {e}")
            return None
    
    def delete_record(self, record_id: str) -> bool:
        """
        删除DNS记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        try:
            self._request('DELETE', '/api/record', params={'id': record_id})
            logger.info(f"成功删除DNS记录 (ID: {record_id})")
            return True
        except Exception as e:
            logger.error(f"删除DNS记录失败: {e}")
            return False
    
    def update_record_status(self, record_id: str, disable: bool) -> bool:
        """
        修改DNS记录状态
        
        注意：更新DNS记录可能存在较长时延，如果需要快速生效，请使用'删除记录-添加记录'方式。
        
        Args:
            record_id: 记录ID
            disable: 是否禁用
            
        Returns:
            是否修改成功
        """
        payload = {
            'id': record_id,
            'disable': disable
        }
        
        try:
            self._request('PUT', '/api/recordDisable', json=payload)
            status = "禁用" if disable else "启用"
            logger.info(f"成功{status}DNS记录 (ID: {record_id})")
            return True
        except Exception as e:
            logger.error(f"修改DNS记录状态失败: {e}")
            return False
    
    def find_txt_records(
        self,
        domain_id: str,
        host: str,
        value: Optional[str] = None
    ) -> List[Dict]:
        """
        查找TXT记录
        
        Args:
            domain_id: 域名ID
            host: 主机头
            value: 记录值（可选）
            
        Returns:
            匹配的TXT记录列表
        """
        return self.get_record_list(
            domain_id=domain_id,
            record_type='TXT',
            host=host,
            data=value
        )
    
    def add_txt_record(
        self,
        domain_id: str,
        host: str,
        value: str,
        ttl: int = 600
    ) -> Optional[str]:
        """
        添加TXT记录（用于ACME验证）
        
        Args:
            domain_id: 域名ID
            host: 主机头
            value: TXT记录值
            ttl: TTL值（默认600秒，10分钟）
            
        Returns:
            新记录的ID，失败返回None
        """
        logger.info(f"添加TXT记录: {host} -> {value}")
        return self.add_record(
            domain_id=domain_id,
            record_type='TXT',
            host=host,
            data=value,
            ttl=ttl
        )
    
    def delete_txt_records(self, domain_id: str, host: str) -> int:
        """
        删除指定主机头的所有TXT记录
        
        Args:
            domain_id: 域名ID
            host: 主机头
            
        Returns:
            删除的记录数量
        """
        records = self.find_txt_records(domain_id, host)
        deleted_count = 0
        
        for record in records:
            if self.delete_record(record['id']):
                deleted_count += 1
        
        logger.info(f"删除了 {deleted_count} 条TXT记录")
        return deleted_count
    
    def update_txt_record(
        self,
        domain_id: str,
        host: str,
        new_value: str,
        ttl: int = 600
    ) -> Optional[str]:
        """
        更新TXT记录（删除旧记录，添加新记录）
        
        注意：为什么不采用'更新记录'API？
        因为更新记录API的时延很长且不稳定，所以为了保证域名记录快速生效，使用'删除记录-添加记录'的方式。
        
        Args:
            domain_id: 域名ID
            host: 主机头
            new_value: 新的TXT记录值
            ttl: TTL值
            
        Returns:
            新记录的ID，失败返回None
        """
        logger.info(f"更新TXT记录: {host}")
        
        # 删除旧记录
        self.delete_txt_records(domain_id, host)
        
        # 添加新记录
        return self.add_txt_record(domain_id, host, new_value, ttl)
    
    def wait_for_propagation(self, seconds: int = 120):
        """
        等待DNS记录生效
        
        Args:
            seconds: 等待时间（秒）
        """
        logger.info(f"等待DNS记录生效（{seconds}秒）...")
        time.sleep(seconds)
        logger.info("DNS记录应该已经生效")


if __name__ == '__main__':
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 初始化客户端
    client = DNSLAClient(
        api_id="3731517a6e365a52776b3a003a31515330724c",
        api_secret="7ad4ca3e8fe258780397df3fd226e427cf884d83"
    )
    
    # 测试获取域名信息
    domain_info = client.get_domain_info("rho.im")
    if domain_info:
        print(f"域名ID: {domain_info['id']}")
        print(f"域名: {domain_info['displayDomain']}")
    
    # 测试获取记录列表
    records = client.get_record_list(domain_id="5435272")
    print(f"\n当前DNS记录数: {len(records)}")
    for record in records[:3]:  # 只显示前3条
        print(f"  - {record['displayHost']}.{record.get('displayData', '')[:50]}")
