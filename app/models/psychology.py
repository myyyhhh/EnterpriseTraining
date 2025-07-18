from pydantic import BaseModel
from typing import List, Literal

class QuestionOption(BaseModel):
    """题目选项模型"""
    option: Literal["A", "B", "C", "D"]  # 选项标识
    text: str  # 选项文本
    score: Literal[4, 3, 2, 1]  # 选项分数

class Question(BaseModel):
    """单个题目模型"""
    id: int  # 题目ID (1-10)
    content: str  # 题目内容
    options: List[QuestionOption]  # 选项列表(固定4个)

class ScoreRange(BaseModel):
    """评分区间模型"""
    min: Literal[10, 16, 26]  # 区间最小值
    max: Literal[15, 25, 40]  # 区间最大值
    assessment: str  # 评估结论
    suggestion: str  # 建议文本

class Dimension(BaseModel):
    """测评维度模型"""
    name: Literal[
        "情绪压力指标", 
        "躯体反应指标", 
        "睡眠认知偏差指标", 
        "运动压力值指标"
    ]  # 维度名称
    questions: List[Question]  # 维度下的题目(10题)
    ranges: List[ScoreRange]  # 评分标准(3个区间)

class PsychologyQuestions(BaseModel):
    """心理试卷总模型"""
    title: str  # 测评标题
    dimensions: List[Dimension]  # 所有维度(4个)