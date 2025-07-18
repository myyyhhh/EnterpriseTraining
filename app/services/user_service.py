from ..models.user import User, UserAccountInfo, UserBasedInfo, UserHabitInfo, UserPsychology
from ..config import users_db
import secrets

def authenticate_user(username: str, password: str) -> Optional[User]:
    """验证用户登录"""
    user = users_db.get(username)
    if user and user.user_account_info.password == password:
        return user
    return None

def create_user(username: str, password: str) -> User:
    """创建新用户"""
    if username in users_db:
        raise ValueError("用户名已存在")
    user = User(
        user_account_info=UserAccountInfo(username=username, password=password),
        user_based_info=UserBasedInfo(),
        user_habit_info=UserHabitInfo(),
        user_psychology=UserPsychology()
    )
    users_db[username] = user
    return user

def update_user_info(username: str, updated_data: dict) -> User:
    """更新用户信息（合并新旧数据）"""
    user = users_db[username]
    # 实际项目建议用Pydantic的model_copy更新，这里简化处理
    for key, value in updated_data.items():
        setattr(user, key, value)
    return user

def test_init():
    """初始化测试数据"""
    from datetime import date
    test_user = User(
        user_account_info=UserAccountInfo(username="test_user_001", password="123456"),
        user_based_info=UserBasedInfo(
            real_name="张三", gender=1, birthday=date(1990, 5, 15), height=175.5, weight=70.3
        ),
        user_habit_info=UserHabitInfo(
            daily_water=1.8, sleep_duration=7.5, exercise_amount="每周3次"
        ),
        user_psychology=UserPsychology()
    )
    users_db["test_user_001"] = test_user