from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from ..dependencies import require_current_user
from ..services.psychology_service import calculate_test_result
from ..main import psychology_questions

router = APIRouter()

@router.post("/submit-test")
async def submit_test(request: Request, current_user=Depends(require_current_user)):
    data = await request.json()
    results = calculate_test_result(data.get("answers", {}))
    
    # 更新用户心理信息（简化版）
    current_user.user_psychology = {r["dimension"]: r["assessment"] for r in results}
    return JSONResponse({"status": "success", "results": results})