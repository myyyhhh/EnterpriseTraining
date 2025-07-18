from fastapi import APIRouter, Form, Depends
from fastapi.responses import JSONResponse
from ..dependencies import require_current_user
from ..config import chat_history
from ..services.ai_service import generate_text
from datetime import datetime

router = APIRouter()

@router.post("/send-message")
async def send_message(
    message: str = Form(...),
    current_user = Depends(require_current_user)
):
    username = current_user.user_account_info.username
    try:
        ai_answer, chat_history = generate_text(message, username)
        return JSONResponse({
            "status": "success",
            "ai_message": {"sender": "ai", "message": ai_answer, "time": datetime.now().strftime("%H:%M:%S")}
        })
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)