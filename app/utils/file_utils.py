import json
import logging
from pathlib import Path
from typing import Dict
from models.psychology import PsychologyQuestions

def load_psychology_assessment(json_path: Path) -> Dict:
    """加载心理测评JSON文件"""
    # 处理路径
    if not json_path.is_absolute():
        json_path = Path.cwd() / json_path
    
    # 检查文件
    if not json_path.exists():
        raise FileNotFoundError(f"文件不存在: {json_path}")
    
    # 读取并解析
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 验证结构
        required = {"title", "dimensions"}
        if not required.issubset(data.keys()):
            raise ValueError(f"缺少必要字段: {required - data.keys()}")
        return data
    except json.JSONDecodeError:
        raise ValueError(f"JSON格式错误: {json_path}")
    except Exception as e:
        raise RuntimeError(f"加载文件失败: {str(e)}")

def assessment_data2BaseModels(assessment_data: Dict) -> PsychologyQuestions:
    """将字典转换为Pydantic模型"""
    return PsychologyQuestions(**assessment_data)