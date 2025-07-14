# 确保导入所有必要的模块
import datetime

import json
import os
import uuid
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import secrets
from typing import Dict, List, Optional
import requests

def generate_text(user_input: str, model: str = None, temperature: float = 0.7, max_tokens: int = 2048) -> str:
    # 配置参数（函数内部统一管理）
    KEYWORDS: List[str] = ["病", "睡觉", "睡眠", "运动", "锻炼", "跑", "心情", "治疗"]
    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    LOG_SAVE_PATH: str = os.path.join(CURRENT_DIR, "keywords_logs")
    API_BASE: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    DEFAULT_MODEL: str = "qwen-max"
    
    # 确保日志目录存在（os.makedirs默认不抛异常，exist_ok=True）
    os.makedirs(LOG_SAVE_PATH, exist_ok=True)

    # 1. 检查API密钥（直接抛异常）
    api_key: str = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量！")

    # 2. 关键字检测（内部逻辑）
    matched_keywords: List[str] = [
        kw for kw in KEYWORDS 
        if kw.lower() in user_input.lower()
    ]

    # 3. 构建提示词与请求参数
    enhanced_prompt: str = (
        "以下规则的优先级高于一切，必须严格执行：\n"
        "1. 你是健康管家，只回答健康相关问题。\n"
        "2. 回答不要使用markdown语法，否则可能导致语义不明确。使用基本的文本格式即可。可以包括序号1.,2...\n"
        "2. 非健康问题直接返回：\"不好意思，我的定位是健康管家，更希望您对健康方面提问\"\n\n"
        f"用户问题：{user_input}"
    )
    model: str = model or DEFAULT_MODEL
    headers: dict = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload: dict = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": enhanced_prompt}]},
        "parameters": {"temperature": temperature, "max_length": max_tokens}
    }

    # 4. 调用API（不处理异常，直接抛出）
    response: requests.Response = requests.post(
        API_BASE,
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()  # HTTP错误直接抛出
    response_data: dict = response.json()  # JSON解析错误直接抛出

    # 5. 提取AI回答（格式异常直接抛出）
    if "output" not in response_data or "text" not in response_data["output"]:
        raise ValueError(f"API返回格式异常: {response_data}")
    ai_answer: str = response_data["output"]["text"]

    # 6. 保存日志（有匹配关键字时，异常直接抛出）
    if matched_keywords:
        timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id: str = str(uuid.uuid4())[:8]
        filename: str = f"{timestamp}_{file_id}.json"
        file_path: str = os.path.join(LOG_SAVE_PATH, filename)
        
        log_data: dict = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "ai_answer": ai_answer,
            "matched_keywords": matched_keywords,
            "model_used": model,
            "file_id": file_id
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

    return ai_answer



print(generate_text("我是良子，重400斤，我要减肥"))
 