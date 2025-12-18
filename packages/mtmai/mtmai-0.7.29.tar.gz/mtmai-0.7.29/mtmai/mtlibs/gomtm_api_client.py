import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class GomtmApiClient:
    """Gomtm API客户端，用于调用gomtm v2 API"""
    
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers
        
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}/api/v2/{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = await self.client.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = await self.client.put(url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = await self.client.patch(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
                
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"API请求失败: {method} {url} - {e}")
            raise
            
    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """获取智能体信息"""
        return await self._make_request("GET", f"agents/{agent_id}")
        
    async def update_agent(self, agent_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新智能体信息"""
        return await self._make_request("PATCH", f"agents/{agent_id}", update_data)
        
    async def update_agent_state(self, agent_id: str, state: Dict[str, Any], 
                                status: Optional[str] = None) -> Dict[str, Any]:
        """更新智能体状态"""
        update_data = {"state": state}
        if status:
            update_data["status"] = status
        return await self.update_agent(agent_id, update_data)
        
    async def emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """发送事件"""
        event_data = {
            "event": event_name,
            "data": data
        }
        await self._make_request("POST", "events", event_data)


def http_url_to_ws_url(http_url: str) -> str:
    """将HTTP URL转换为WebSocket URL"""
    if http_url.startswith("https://"):
        return http_url.replace("https://", "wss://")
    elif http_url.startswith("http://"):
        return http_url.replace("http://", "ws://")
    else:
        return http_url
