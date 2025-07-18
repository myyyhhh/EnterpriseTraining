from typing import Dict, List
from models.psychology import PsychologyQuestions, Dimension

from config import PSYCHOLOGY_ASSESSMENT_PATH
from utils.file_utils import load_psychology_assessment, assessment_data2BaseModels

def load_psychology_questions() -> PsychologyQuestions:
    """加载心理测评题目"""
    assessment_data = load_psychology_assessment(PSYCHOLOGY_ASSESSMENT_PATH)
    return assessment_data2BaseModels(assessment_data)

def calculate_assessment_results(answers: Dict[str, Dict]) -> List[Dict]:
    """计算测评结果"""
    questions = load_psychology_questions()
    results = []
    
    # 清洗答案键（去除空格）
    cleaned_answers = {
        k.replace(" ", ""): v for k, v in answers.items()
    }
    
    # 计算每个维度得分
    for dimension in questions.dimensions:
        dim_name = dimension.name
        total_score = 0
        
        # 累加题目分数
        for question in dimension.questions:
            answer_key = f"{dim_name}-{question.id}".replace(" ", "")
            if answer_key in cleaned_answers:
                total_score += cleaned_answers[answer_key]["score"]
        
        # 匹配评分区间
        assessment = ""
        suggestion = ""
        for score_range in dimension.ranges:
            if score_range.min <= total_score <= score_range.max:
                assessment = score_range.assessment
                suggestion = score_range.suggestion
                break
        
        results.append({
            "dimension": dim_name,
            "score": total_score,
            "assessment": assessment,
            "suggestion": suggestion
        })
    
    return results