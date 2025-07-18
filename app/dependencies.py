from fastapi import Request, HTTPException
from .config import active_users, users_db
from .models.user import User

async def get_current_user(request: Request) -> Optional[User]:
    """获取当前登录用户（供路由依赖使用）"""
    session_id = request.cookies.get("session_id")
    if session_id in active_users:
        username = active_users[session_id]
        return users_db.get(username)
    return None

async def require_current_user(current_user: User = Depends(get_current_user)):
    """强制要求用户登录（用于需要权限的路由）"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")
    return current_user