from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from database import current_user
from services.psychology_service import (
    load_psychology_questions,
    calculate_assessment_results
)
from routers.auth import get_current_user

router = APIRouter(tags=["心理测评"])

# 获取测评题目
@router.get("/psychology-questions")
async def get_questions(user: dict = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    questions = load_psychology_questions()
    return questions.dict()

# 提交测评答案
@router.post("/submit-test")
async def submit_test(
    request: Request,
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    data = await request.json()
    answers = data.get("answers", {})
    if not answers:
        return JSONResponse(
            content={"status": "error", "message": "未提交答案"},
            status_code=400
        )
    
    results = calculate_assessment_results(answers)
    return JSONResponse(content={
        "status": "success",
        "results": results
    })