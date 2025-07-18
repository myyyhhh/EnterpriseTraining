# """
# app/
# ├── main.py               # 应用入口
# ├── config.py             # 配置设置
# ├── database.py           # 数据库相关
# ├── models/               # 数据模型目录
# │   ├── __init__.py
# │   ├── user.py           # 用户模型
# │   └── psychology.py     # 心理测评模型
# ├── routers/              # 路由控制器目录
# │   ├── __init__.py
# │   ├── auth.py           # 认证路由
# │   ├── chat.py           # 聊天路由
# │   ├── user.py           # 用户管理路由
# │   └── psychology.py     # 心理测评路由
# ├── services/             # 业务逻辑服务
# │   ├── __init__.py
# │   ├── auth_service.py   # 认证服务
# │   ├── chat_service.py   # 聊天服务
# │   ├── user_service.py   # 用户服务
# │   └── psychology_service.py # 心理测评服务
# ├── utils/                # 工具函数
# │   ├── __init__.py
# │   ├── ai_utils.py       # AI相关工具
# │   └── file_utils.py     # 文件操作工具
# ├── static/               # 静态文件
# └── templates/            # 模板文件

# """

# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pathlib import Path

# from app.config import STATIC_DIR, TEMPLATE_DIR
# from app.routers import auth, chat, user, psychology


# # 创建FastAPI应用
# app = FastAPI(title="健康管理系统")

# # 挂载静态文件
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# # 配置模板
# templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# # 包含路由
# app.include_router(auth.router)
# app.include_router(chat.router)
# app.include_router(user.router)
# app.include_router(psychology.router)

# # 首页路由
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
