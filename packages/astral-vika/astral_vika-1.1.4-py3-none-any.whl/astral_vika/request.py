"""
维格表HTTP请求处理模块

兼容原vika.py库的请求处理方式
"""
import httpx
import urllib.parse
import json
from typing import Dict, Any, Optional, Callable, Awaitable

from .const import DEFAULT_API_BASE, FUSION_API_PREFIX
from .exceptions import VikaException, create_exception_from_response
from .utils import build_api_url, handle_response


class Session:
    """
    一个原生异步的HTTP请求会话，使用httpx库。
    """

    def __init__(self, token: str, api_base: str = DEFAULT_API_BASE, status_callback: Optional[Callable[[str], Awaitable[None]]] = None, verify_ssl: bool = True):
        # 将token存为私有字段以避免泄露
        self._token = token
        self.api_base = api_base.rstrip('/')
        self.status_callback = status_callback
        self.verify_ssl = verify_ssl
        headers = {
            # 仅用于请求头注入，不在属性/日志中明文暴露
            'Authorization': f'Bearer {self._token}',
            'Content-Type': 'application/json',
        }
        self.client = httpx.AsyncClient(headers=headers, timeout=30.0, verify=verify_ssl)

    def _build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        if endpoint.startswith('http'):
            return endpoint

        if not endpoint.startswith('/fusion'):
            endpoint = f"{FUSION_API_PREFIX.rstrip('/')}/{endpoint.lstrip('/')}"
        else:
            # 如果已经是完整的 /fusion/vX/ 路径，则直接使用
            pass

        return build_api_url(self.api_base, endpoint)

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        发送HTTP请求（异步）
        """
        url = self._build_url(endpoint)
        
        # 创建 params 的副本以避免修改原始字典，防止状态污染
        final_params = params.copy() if params else {}

        try:
            if self.status_callback:
                await self.status_callback(f"正在向 {url} 发送 {method} 请求...")
            response = await self.client.request(
                method=method.upper(),
                url=url,
                params=final_params,  # 使用副本
                json=json_body,
                data=data,
                files=files,
                headers=headers,  # 允许覆盖默认头
            )

            # raise_for_status 会在 4xx 或 5xx 响应时引发 HTTPStatusError
            response.raise_for_status()

            if self.status_callback:
                await self.status_callback(f"成功接收到来自 {url} 的响应。")

            try:
                response_data = response.json()
            except json.JSONDecodeError:
                # 解析失败时抛异常以统一错误语义并避免返回临时结构
                raw_text = response.text or ""
                snippet = raw_text[:128]
                message = f"Response parsing error: {snippet}"
                raise create_exception_from_response({'message': message, 'code': response.status_code}, response.status_code)

            return handle_response(response_data, response.status_code)

        except httpx.HTTPStatusError as e:
            raise VikaException(
                f"HTTP error: {e.response.status_code} - {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise VikaException(f"Network error: {str(e)}") from e

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.request('GET', endpoint, params=params)

    async def aget(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return await self.request('GET', endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json_body: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        return await self.request('POST', endpoint, json_body=json_body, data=data, files=files)

    async def patch(self, endpoint: str, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.request('PATCH', endpoint, json_body=json_body)

    async def put(self, endpoint: str, json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.request('PUT', endpoint, json_body=json_body)

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.request('DELETE', endpoint, params=params)

    async def close(self) -> None:
        """关闭客户端会话"""
        await self.client.aclose()

    async def __aenter__(self) -> 'Session':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def __repr__(self) -> str:
        # 避免在调试/日志中泄露敏感token，仅展示非敏感状态
        return f"Session(api_base='{self.api_base}')"

    def __str__(self) -> str:
        # 仅展示非敏感信息
        return f"Session({self.api_base})"


__all__ = ['Session']
