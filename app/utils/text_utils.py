from ..models.user import User

def build_prompt(user_info: User) -> str:
    """构建健康建议的提示词"""
    # 基本信息拼接（简化版，保留核心逻辑）
    gender_title = "先生" if user_info.user_based_info.gender == 1 else "女士" if user_info.user_based_info.gender == 2 else "朋友"
    name = user_info.user_based_info.real_name or user_info.user_account_info.username or "用户"
    
    return f"""请以健康管家身份，为{name}{gender_title}提供建议。
    基本信息：{user_info.user_based_info.model_dump()}
    习惯信息：{user_info.user_habit_info.model_dump()}
    心理状态：{user_info.user_psychology.model_dump()}
    要求：分运动、饮食、睡眠、心理四方面，用@和&包裹每个建议。
    """

def extract_advice(ai_response: str) -> list[str]:
    """从AI回复中提取建议（使用正则匹配@和&标记）"""
    import re
    return re.findall(r'@([^&]+)&', ai_response)