import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 静态文件目录
STATIC_DIR = BASE_DIR / "static"

# 模板文件目录
TEMPLATE_DIR = BASE_DIR / "templates"

# 心理测评JSON文件路径
PSYCHOLOGY_ASSESSMENT_PATH = STATIC_DIR / "mental_health_assessment.json"

# AI配置
AI_MODEL = "qwen-max"
AI_TEMPERATURE = 0.7
AI_MAX_TOKENS = 2048
AI_API_BASE = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 日志配置
LOG_SAVE_PATH = BASE_DIR / "keywords_logs"