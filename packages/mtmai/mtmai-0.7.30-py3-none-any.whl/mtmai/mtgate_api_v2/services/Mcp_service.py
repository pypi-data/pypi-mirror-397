from typing import *

import httpx

from ..api_config import APIConfig, HTTPException
from ..models import *


def McpApiHello(api_config_override: Optional[APIConfig] = None, *, msg: str) -> Dict[str, Any]:
    api_config = api_config_override if api_config_override else APIConfig()

    base_path = api_config.base_path
    path = f"/api/cf/mcpapi/hello"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer { api_config.get_access_token() }",
    }
    query_params: Dict[str, Any] = {"msg": msg}

    query_params = {key: value for (key, value) in query_params.items() if value is not None}

    with httpx.Client(base_url=base_path, verify=api_config.verify) as client:
        response = client.request(
            "get",
            httpx.URL(path),
            headers=headers,
            params=query_params,
        )

    if response.status_code != 200:
        raise HTTPException(response.status_code, f"McpApiHello failed with status code: {response.status_code}")
    else:
        body = None if 200 == 204 else response.json()

    return body
