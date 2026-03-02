"""认证路由：仅登录（测试账号写死）。"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import LoginRequest, LoginResponse, UserProfile
from app.security import (
    CurrentUser,
    authenticate_test_user,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    """测试登录接口（不包含注册和订阅流程）。"""
    user = authenticate_test_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = create_access_token(user)
    profile = UserProfile(
        id=user["id"],
        username=user["username"],
        display_name=user["display_name"],
        membership=user["membership"],
        level=user["level"],
    )
    return LoginResponse(access_token=token, user=profile)


@router.get("/me", response_model=UserProfile)
async def me(current_user: CurrentUser = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        display_name=current_user.display_name,
        membership=current_user.membership,
        level=current_user.level,
    )
