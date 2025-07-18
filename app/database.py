from typing import Dict, List, Optional
from app.models.user import User

# 模拟数据库 - 实际应用中替换为真实数据库

# 用户数据存储 (username: User)
users_db: Dict[str, User] = {}

# 活跃用户 (session_id: username)
active_users: Dict[str, str] = {}

# 对话历史 (username: [message1, message2,...])
chat_history: Dict[str, List[Dict[str, str]]] = {}

# 当前登录用户（内存临时存储）
current_user: Optional[User] = None