from typing import List, Optional
from models.user import User

from database import users_db

def get_user(username: str) -> Optional[User]:
    """获取用户信息"""
    return users_db.get(username)

def get_all_users() -> List[User]:
    """获取所有用户"""
    return list(users_db.values())

def update_user_info(username: str, updated_user: User) -> User:
    """更新用户信息"""
    if username not in users_db:
        raise ValueError("用户不存在")
    
    users_db[username] = updated_user
    return updated_user

def generate_health_advice(user: User) -> str:
    """生成健康建议"""
    from utils.ai_utils import build_prompt, subjection
    return subjection(user)


def get_current_user