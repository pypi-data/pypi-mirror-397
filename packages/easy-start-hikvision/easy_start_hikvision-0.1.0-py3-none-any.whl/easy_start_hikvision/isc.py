#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
海康威视 ISecureCenter API 客户端模块
该模块提供了与海康威视 ISecureCenter 平台交互的功能，支持同步和异步请求方式
"""

import base64
import hashlib
import hmac
import uuid
from datetime import datetime

import httpx


class ISecureCenter:
    """
    海康威视 ISecureCenter API 客户端类
    用于与海康威视 ISecureCenter 平台进行交互，提供签名生成和请求发送功能
    """
    
    def __init__(
            self,
            host: str = "",
            ak: str = "",
            sk: str = ""
    ):
        """
        初始化 ISecureCenter API 客户端
        
        参数:
            host (str): API 服务器地址
            ak (str): 访问密钥 Access Key
            sk (str): 密钥 Secret Key
        """
        # 处理主机地址末尾的斜杠，确保格式统一
        self.host = host[:-1] if host.endswith("/") else host
        self.ak = ak  # 访问密钥 Access Key
        self.sk = sk  # 密钥 Secret Key

    def timestamp(self):
        """
        生成当前时间戳（毫秒）
        
        返回:
            int: 当前时间戳（毫秒）
        """
        return int(datetime.now().timestamp() * 1000)

    def nonce(self):
        """
        生成随机的 UUID 字符串
        
        返回:
            str: 随机的 UUID 字符串（无连字符）
        """
        return uuid.uuid4().hex

    def signature(self, string: str = ""):
        """
        生成请求签名
        
        参数:
            string (str): 需要签名的字符串
            
        返回:
            str: 生成的签名（Base64 编码的 HMAC-SHA256 哈希值）
        """
        return base64.b64encode(
            hmac.new(
                self.sk.encode(),  # 使用密钥 Secret Key
                string.encode(),   # 待签名字符串
                digestmod=hashlib.sha256  # 使用 SHA256 哈希算法
            ).digest()
        ).decode()

    def headers(
            self,
            method: str = "POST",
            path: str = "",
            headers: dict = {}
    ):
        """
        生成请求头
        
        参数:
            method (str): HTTP 请求方法，默认 POST
            path (str): 请求路径
            headers (dict): 额外的请求头
            
        返回:
            dict: 完整的请求头字典
        """
        method = method if isinstance(method, str) else "POST"
        path = path if isinstance(path, str) else ""
        headers = headers if isinstance(headers, dict) else dict()
        
        # 构建基础请求头
        headers = {
            "accept": "*/*",  # 接受所有响应类型
            "content-type": "application/json",  # 内容类型为 JSON
            "x-ca-signature-headers": "x-ca-key,x-ca-nonce,x-ca-timestamp",  # 参与签名的请求头
            "x-ca-key": self.ak,  # 访问密钥 Access Key
            "x-ca-nonce": self.nonce(),  # 随机 UUID
            "x-ca-timestamp": str(self.timestamp()),  # 当前时间戳
            **headers  # 合并额外的请求头
        }
        
        # 构建待签名字符串
        string = "\n".join([
            method,
            headers["accept"],
            headers["content-type"],
            f"x-ca-key:{headers['x-ca-key']}",
            f"x-ca-nonce:{headers['x-ca-nonce']}",
            f"x-ca-timestamp:{headers['x-ca-timestamp']}",
            path,
        ])
        
        # 添加签名到请求头
        headers["x-ca-signature"] = self.signature(string=string)
        return headers

    def client(self, **kwargs):
        """
        创建同步 HTTP 客户端
        
        参数:
            **kwargs: 传递给 httpx.Client 的额外参数
            
        返回:
            httpx.Client: 配置好的同步 HTTP 客户端
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        kwargs.setdefault("base_url", self.host)  # 设置基础 URL
        kwargs.setdefault("timeout", 120)  # 设置超时时间为 120 秒
        kwargs.setdefault("verify", False)  # 不验证 SSL 证书
        return httpx.Client(**kwargs)

    def async_client(self, **kwargs):
        """
        创建异步 HTTP 客户端
        
        参数:
            **kwargs: 传递给 httpx.AsyncClient 的额外参数
            
        返回:
            httpx.AsyncClient: 配置好的异步 HTTP 客户端
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        kwargs.setdefault("base_url", self.host)  # 设置基础 URL
        kwargs.setdefault("timeout", 120)  # 设置超时时间为 120 秒
        kwargs.setdefault("verify", False)  # 不验证 SSL 证书
        return httpx.AsyncClient(**kwargs)

    def request(self, client: httpx.Client = None, **kwargs):
        """
        发送同步 API 请求
        
        参数:
            client (httpx.Client): 可选的 HTTP 客户端，如果不提供则创建新客户端
            **kwargs: 传递给 client.request 的额外参数
            
        返回:
            tuple: (请求是否成功, 响应 JSON 数据, 原始响应对象)
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        kwargs.setdefault("method", "POST")  # 默认使用 POST 方法
        kwargs.setdefault("url", "")  # 默认 URL 为空
        kwargs.setdefault("headers", dict())  # 默认请求头为空字典
        
        # 生成请求头
        headers = self.headers(
            method=kwargs.get("method", "POST"),
            path=kwargs.get("url", ""),
            headers=kwargs.get("headers", dict())
        )
        kwargs["headers"] = headers
        
        response: httpx.Response = None  # 用于存储 API 响应对象
        
        # 如果没有提供客户端，则创建新客户端并使用上下文管理器
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        
        # 解析响应 JSON 数据，如果请求失败则返回空字典
        response_json = response.json() if response.is_success else dict()
        # 返回(请求是否成功, 响应 JSON, 原始响应)
        return int(response_json.get("code", 1)) == 0, response_json, response

    async def async_request(self, client: httpx.AsyncClient = None, **kwargs):
        """
        发送异步 API 请求
        
        参数:
            client (httpx.AsyncClient): 可选的异步 HTTP 客户端，如果不提供则创建新客户端
            **kwargs: 传递给 client.request 的额外参数
            
        返回:
            tuple: (请求是否成功, 响应 JSON 数据, 原始响应对象)
        """
        kwargs = kwargs if isinstance(kwargs, dict) else dict()
        kwargs.setdefault("method", "POST")  # 默认使用 POST 方法
        kwargs.setdefault("url", "")  # 默认 URL 为空
        kwargs.setdefault("headers", dict())  # 默认请求头为空字典
        
        # 生成请求头
        headers = self.headers(
            method=kwargs.get("method", "POST"),
            path=kwargs.get("url", ""),
            headers=kwargs.get("headers", dict())
        )
        kwargs["headers"] = headers
        
        response: httpx.Response = None  # 用于存储 API 响应对象
        
        # 如果没有提供客户端，则创建新客户端并使用上下文管理器
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        
        # 解析响应 JSON 数据，如果请求失败则返回空字典
        response_json = response.json() if response.is_success else dict()
        # 返回(请求是否成功, 响应 JSON, 原始响应)
        return int(response_json.get("code", 1)) == 0, response_json, response