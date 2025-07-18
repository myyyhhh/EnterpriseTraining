from typing import Optional
from app.models.user import User, UserAccountInfo, UserBasedInfo, UserHabitInfo, UserPsychology

def authenticate_user(username: str, password: str) -> Optional[User]:
    """验证用户登录"""
    # 测试用户
    if username == "123" and password == "321":
        return User(
            user_account_info=UserAccountInfo(username=username, password=password),
            user_based_info=UserBasedInfo(),
            user_habit_info=UserHabitInfo(),
            user_psychology=UserPsychology()
        )
    
    # 数据库用户验证
    from app.database import users_db
    if username in users_db:
        user = users_db[username]
        if user.user_account_info.password == password:
            return user
    
    return None

def sign_up(username: str, password: str) -> User:
    """用户注册"""
    return User(
        user_account_info=UserAccountInfo(username=username, password=password),
        user_based_info=UserBasedInfo(),
        user_habit_info=UserHabitInfo(),
        user_psychology=UserPsychology()
    )