"""认证相关工具：写死测试账号 + 简单 Bearer Token。"""

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

TEST_USERS = {
    "test_vip": {
        "id": "u_test_vip_001",
        "username": "test_vip",
        "password": "123456",
        "display_name": "VIP 测试用户",
        "membership": "vip",
        "level": 2,
    },
    "test_free": {
        "id": "u_test_free_001",
        "username": "test_free",
        "password": "123456",
        "display_name": "免费测试用户",
        "membership": "free",
        "level": 0,
    },
}

TOKEN_EXPIRE_SECONDS = int(os.getenv("TOKEN_EXPIRE_SECONDS", "2592000"))  # 默认 30 天
AUTH_SECRET = os.getenv("AUTH_SECRET", "dev-only-secret-change-in-prod")
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    username: str
    display_name: str
    membership: str
    level: int


def _encode_base64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _decode_base64url(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(value: str) -> str:
    digest = hmac.new(AUTH_SECRET.encode(), value.encode(), hashlib.sha256).digest()
    return _encode_base64url(digest)


def create_access_token(user: dict) -> str:
    payload = {
        "sub": user["id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "membership": user["membership"],
        "level": user["level"],
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }
    payload_raw = _encode_base64url(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(payload_raw)
    return f"{payload_raw}.{signature}"


def verify_access_token(token: str) -> CurrentUser:
    try:
        payload_raw, signature = token.split(".", maxsplit=1)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效 token") from exc

    expected_signature = _sign(payload_raw)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 签名错误")

    try:
        payload = json.loads(_decode_base64url(payload_raw))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 解析失败") from exc

    exp = int(payload.get("exp", 0))
    if exp < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 已过期")

    return CurrentUser(
        id=str(payload["sub"]),
        username=str(payload["username"]),
        display_name=str(payload["display_name"]),
        membership=str(payload["membership"]),
        level=int(payload["level"]),
    )


def authenticate_test_user(username: str, password: str) -> dict | None:
    user = TEST_USERS.get(username)
    if not user or user["password"] != password:
        return None
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少认证信息")
    return verify_access_token(credentials.credentials)
