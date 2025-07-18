from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from app.database import current_user, chat_history
from app.services.chat_service import generate_ai_response
from app.routers.auth import get_current_user  # 复用认证逻辑

router = APIRouter(tags=["聊天"])

# 发送消息
@router.post("/send-message")
async def send_message(
    request: Request,
    message: str = Form(...),
    user: dict = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    username = user["username"]
    try:
        # 调用AI服务生成回答
        ai_answer, updated_history = generate_ai_response(
            user_input=message,
            current_user=username,
            chat_history=chat_history
        )
        chat_history.update(updated_history)  # 更新全局对话历史

        return JSONResponse(content={
            "status": "success",
            "user_message": {
                "sender": "human",
                "message": message,
                "time": datetime.now().strftime("%H:%M:%S")
            },
            "ai_message": {
                "sender": "ai",
                "message": ai_answer,
                "time": datetime.now().strftime("%H:%M:%S")
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"消息处理失败: {str(e)}")