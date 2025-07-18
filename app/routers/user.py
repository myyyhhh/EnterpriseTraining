from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from database import users_db, current_user
from models.user import User
from services.user_service import update_user_info, get_all_users
from routers.auth import get_current_user

router = APIRouter(tags=["用户管理"])

# 获取所有用户
@router.get("/users")
async def list_users(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    return [user.dict() for user in get_all_users()]

# 更新用户信息
@router.post("/update-user-info")
async def update_info(
    updated_user: User,
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    username = user["username"]
    try:
        updated = update_user_info(username, updated_user)
        return JSONResponse(content={
            "status": "success",
            "message": "信息更新成功",
            "user_info": updated.dict()
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 添加用户（管理员功能）
@router.post("/add-user")
async def add_user(
    new_username: str,
    new_password: str,
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    if new_username in users_db:
        return JSONResponse(
            content={"status": "error", "message": "用户名已存在"}
        )
    
    from services.auth_service import sign_up
    users_db[new_username] = sign_up(new_username, new_password)
    return JSONResponse(
        content={"status": "success", "message": "用户添加成功"}
    )