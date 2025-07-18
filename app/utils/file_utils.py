import json
import logging
from pathlib import Path
from typing import Dict, Any

def load_psychology_assessment(json_path: str | Path) -> Dict[str, Any]:
    """加载心理测评JSON文件并验证格式"""
    json_path = Path(json_path) if isinstance(json_path, str) else json_path
    if not json_path.is_absolute():
        json_path = Path.cwd() / json_path

    if not json_path.exists():
        raise FileNotFoundError(f"文件不存在: {json_path}")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 基础格式验证
        required = {'title', 'dimensions'}
        if not required.issubset(data.keys()):
            raise ValueError(f"缺少必要字段: {required - data.keys()}")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析失败: {str(e)}")