import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# 路径配置（统一使用pathlib.Path类型）
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"  # 使用Path对象替代os.path.join
TEMPLATE_DIR = BASE_DIR / "templates"
PSYCHOLOGY_JSON_PATH = STATIC_DIR / "mental_health_assessment.json"  # 正确：Path对象可以用/拼接

# AI配置
API_BASE = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
DEFAULT_MODEL = "qwen-max"
KEYWORDS: List[str] = ["病", "睡觉", "睡眠", "运动", "锻炼", "跑", "心情", "治疗"]
LOG_SAVE_PATH = os.path.join(BASE_DIR, "keywords_logs")  # 这里仍可用os.path.join
os.makedirs(LOG_SAVE_PATH, exist_ok=True)

# 全局存储（实际项目建议用数据库）
users_db: Dict[str, Any] = {}  # 用户数据：{username: User对象}
active_users: Dict[str, str] = {}  # 登录会话：{session_id: username}
chat_history: Dict[str, List[Dict[str, str]]] = {}  # 对话历史：{username: [消息列表]}