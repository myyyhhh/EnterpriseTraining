from pydantic import BaseModel
from typing import List, Literal

class QuestionOption(BaseModel):
    option: Literal["A", "B", "C", "D"]
    text: str
    score: Literal[4, 3, 2, 1]

class Question(BaseModel):
    id: int
    content: str
    options: List[QuestionOption]

class ScoreRange(BaseModel):
    min: Literal[10, 16, 26]
    max: Literal[15, 25, 40]
    assessment: str
    suggestion: str

class Dimension(BaseModel):
    name: Literal["情绪压力指标", "躯体反应指标", "睡眠认知偏差指标", "运动压力值指标"]
    questions: List[Question]
    ranges: List[ScoreRange]

class PsychologyQuestions(BaseModel):
    title: str
    dimensions: List[Dimension]