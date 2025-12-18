import os

from hatchet_sdk import Hatchet
from hatchet_sdk.config import ClientConfig

# 使用环境变量配置，优先使用云端Hatchet服务
hatchet_token = os.environ.get("HATCHET_CLIENT_TOKEN")

# 从token中提取服务器URL
hatchet_server_url = None
if hatchet_token:
    try:
        import base64
        import json

        # 解析JWT token获取服务器URL
        parts = hatchet_token.split(".")
        if len(parts) >= 2:
            claims_part = parts[1]
            claims_part += "=" * ((4 - len(claims_part) % 4) % 4)  # Padding
            claims_data = base64.urlsafe_b64decode(claims_part)
            claims = json.loads(claims_data)
            hatchet_server_url = claims.get("server_url")
    except Exception:
        pass

# 如果没有配置或解析失败，使用默认配置
if not hatchet_token or not hatchet_server_url:
    hatchet_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6InNyZGpFZyJ9.eyJhdWQiOiJodHRwOi8vaGF0Y2hldC55dWVwYTguY29tOjg4ODgiLCJleHAiOjQ5MDkxMTI5OTAsImdycGNfYnJvYWRjYXN0X2FkZHJlc3MiOiJoYXRjaGV0Lnl1ZXBhOC5jb206NzA3NyIsImlhdCI6MTc1NTUxMjk5MCwiaXNzIjoiaHR0cDovL2hhdGNoZXQueXVlcGE4LmNvbTo4ODg4Iiwic2VydmVyX3VybCI6Imh0dHA6Ly9oYXRjaGV0Lnl1ZXBhOC5jb206ODg4OCIsInN1YiI6IjcwN2QwODU1LTgwYWItNGUxZi1hMTU2LWYxYzQ1NDZjYmY1MiIsInRva2VuX2lkIjoiNmU4MzVkNDgtNzlkYS00MTg1LTg1MjAtMDM0MWYyMGQ0Y2FkIn0.l-1i7za7QuzZEusYBuGaRpU-5oc6bnNUy0zY5kxNGNlDIxjILfynq4w6TfP4XvdqYFWJQXClaCKwUNzG-0cfOg"
    hatchet_server_url = "http://hatchet.yuepa8.com:8888"

hatchet = Hatchet(
    debug=True,
    config=ClientConfig(
        token=hatchet_token,
        server_url=hatchet_server_url,
    ),
)
