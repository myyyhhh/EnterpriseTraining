from typing import Dict, List, Tuple
from app.utils.ai_utils import generate_text

def generate_ai_response(
    user_input: str,
    current_user: str,
    chat_history: Dict[str, List[Dict[str, str]]]
) -> Tuple[str, Dict[str, List[Dict[str, str]]]]:
    """生成AI回答并更新对话历史"""
    return generate_text(
        user_input=user_input,
        current_user=current_user,
        chat_history=chat_history
    )