#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
停车系统API客户端模块
该模块提供了与停车系统API交互的功能，支持同步和异步请求方式
"""

import hashlib
from datetime import datetime

import httpx


class Pklot:
    """
    停车系统API客户端类
    用于与停车系统API进行交互，提供签名生成和请求发送功能
    """
    
    def __init__(
            self,
            base_url: str = "http://ykt.test.cxyun.net.cn:7303",
            parking_id: str = "",
            app_key: str = "",
    ):
        """
        初始化停车系统API客户端
        
        参数:
            base_url (str): API基础URL，默认值为测试环境地址
            parking_id (str): 停车场ID
            app_key (str): API应用密钥
        """
        # 处理URL末尾的斜杠，确保格式统一
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.parking_id = parking_id  # 停车场ID
        self.app_key = app_key  # API应用密钥

    def client(self, **kwargs):
        """
        创建同步HTTP客户端
        
        参数:
            **kwargs: 传递给httpx.Client的额外参数
            
        返回:
            httpx.Client: 配置好的同步HTTP客户端
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        # 设置默认基础URL
        kwargs.setdefault("base_url", self.base_url)
        # 设置默认超时时间为120秒
        kwargs.setdefault("timeout", 120)
        return httpx.Client(**kwargs)

    def async_client(self, **kwargs):
        """
        创建异步HTTP客户端
        
        参数:
            **kwargs: 传递给httpx.AsyncClient的额外参数
            
        返回:
            httpx.AsyncClient: 配置好的异步HTTP客户端
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        # 设置默认基础URL
        kwargs.setdefault("base_url", self.base_url)
        # 设置默认超时时间为120秒
        kwargs.setdefault("timeout", 120)
        return httpx.AsyncClient(**kwargs)

    def signature(self, data: dict = dict()):
        """
        生成请求签名
        
        参数:
            data (dict): 需要签名的数据字典
            
        返回:
            str: 生成的MD5签名字符串（大写）
        """
        temp_string = ""
        data = data if isinstance(data, dict) else dict()
        
        # 如果有数据需要签名
        if len(data.keys()):
            # 对字典键进行排序
            data_sorted = sorted(data.keys())
            if isinstance(data_sorted, list):
                # 构建待签名字符串
                temp_string = "&".join([
                    f"{i}={data[i]}"
                    for i in data_sorted if i != "appKey"  # 排除appKey字段
                ]) + f"{hashlib.md5(self.app_key.encode('utf-8')).hexdigest().upper()}"
        
        # 生成MD5签名并转换为大写
        return hashlib.md5(temp_string.encode('utf-8')).hexdigest().upper()

    def request(self, client: httpx.Client = None, **kwargs):
        """
        发送同步API请求
        
        参数:
            client (httpx.Client): 可选的HTTP客户端，如果不提供则创建新客户端
            **kwargs: 传递给client.request的额外参数
            
        返回:
            tuple: (请求是否成功, 响应JSON数据, 原始响应对象)
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        # 默认使用POST方法
        kwargs.setdefault("method", "POST")
        # 生成当前时间戳（毫秒）
        timestamp = int(datetime.now().timestamp() * 1000)
        # 默认JSON数据为空字典
        kwargs.setdefault("json", dict())
        
        # 构建请求JSON数据，包含公共参数
        kwargs["json"] = {
            **{
                "parkingId": self.parking_id,
                "timestamp": timestamp,
                "sign": self.signature({
                    "parkingId": self.parking_id,
                    "timestamp": timestamp,
                })
            },
            **kwargs["json"],
        }
        
        response: httpx.Response = None  # 用于存储API响应对象
        
        # 如果没有提供客户端，则创建新客户端并使用上下文管理器
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        
        # 解析响应JSON数据，如果请求失败则返回空字典
        response_json = response.json() if response.is_success else dict()
        # 返回(请求是否成功, 响应JSON, 原始响应)
        return str(response_json.get("status", "0")) == "1", response_json, response

    async def async_request(self, client: httpx.AsyncClient = None, **kwargs):
        """
        发送异步API请求
        
        参数:
            client (httpx.AsyncClient): 可选的异步HTTP客户端，如果不提供则创建新客户端
            **kwargs: 传递给client.request的额外参数
            
        返回:
            tuple: (请求是否成功, 响应JSON数据, 原始响应对象)
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        # 默认使用POST方法
        kwargs.setdefault("method", "POST")
        # 生成当前时间戳（毫秒）
        timestamp = int(datetime.now().timestamp() * 1000)
        # 默认JSON数据为空字典
        kwargs.setdefault("json", dict())
        
        # 构建请求JSON数据，包含公共参数
        kwargs["json"] = {
            **{
                "parkingId": self.parking_id,
                "timestamp": timestamp,
                "sign": self.signature({
                    "parkingId": self.parking_id,
                    "timestamp": timestamp,
                })
            },
            **kwargs["json"],
        }
        
        response: httpx.Response = None  # 用于存储API响应对象
        
        # 如果没有提供客户端，则创建新客户端并使用上下文管理器
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        
        # 解析响应JSON数据，如果请求失败则返回空字典
        response_json = response.json() if response.is_success else dict()
        # 返回(请求是否成功, 响应JSON, 原始响应)
        return str(response_json.get("status", "0")) == "1", response_json, response