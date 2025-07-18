from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import JSONResponse
from ..dependencies import get_current_user, require_current_user
from ..config import users_db, active_users
from ..models.user import User
from ..services.user_service import update_user_info

router = APIRouter()

@router.post("/switch-user")
async def switch_user(target_user: str = Form(...), current_user=Depends(require_current_user)):
    if target_user not in users_db:
        return JSONResponse({"status": "error", "message": "用户不存在"}, status_code=404)
    # 更新会话（简化版）
    return JSONResponse({"status": "success", "username": target_user})

@router.post("/update-user-info")
async def update_info(updated_user: User, current_user=Depends(require_current_user)):
    updated = update_user_info(current_user.user_account_info.username, updated_user.dict())
    return {"status": "success", "user": updated.dict()}