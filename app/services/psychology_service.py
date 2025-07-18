from ..models.psychology import PsychologyQuestions
from ..config import psychology_questions  # 从main.py导入全局题目数据

def calculate_test_result(answers: dict) -> list[dict]:
    """计算心理测试结果（根据答案匹配得分区间）"""
    results = []
    for dimension in psychology_questions.dimensions:
        total_score = sum(answers.get(f"{dimension.name}-{q.id}", {}).get("score", 0) for q in dimension.questions)
        # 匹配得分区间
        for r in dimension.ranges:
            if r.min <= total_score <= r.max:
                results.append({
                    "dimension": dimension.name,
                    "score": total_score,
                    "assessment": r.assessment,
                    "suggestion": r.suggestion
                })
                break
    return results