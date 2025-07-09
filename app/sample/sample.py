import base64
import uuid
from datetime import date
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from cryptography.fernet import Fernet
import matplotlib.pyplot as plt
import io
import json

# 生成加密密钥（实际应用中应安全存储）
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
# /static：这是URL路径前缀，表示所有以/static开头的请求都会被交给StaticFiles处理。
# StaticFiles(directory="static")：指定静态文件存放的目录为static。也就是说，static文件夹中的所有文件都可以通过/static路径来访问。
# name="static"：为挂载的静态文件设置一个名称，可以方便地引用。


templates = Jinja2Templates(directory="templates")
# /templates：这是模板文件存放的目录，FastAPI会在这个目录下查找HTML模板文件。


# 内存数据库（实际应用中应使用持久化存储）
# 使用假名化ID作为键
health_db = {}
user_settings = {}

# 数据模型
class HealthData(BaseModel):
    height: float
    weight: float
    sleep_hours: float
    exercise_minutes: int
    mood: int  # 1-5评分
    diet_quality: int  # 1-5评分
    date: str = date.today().isoformat()

# 加密函数
def encrypt_data(data: dict) -> str:
    json_data = json.dumps(data)
    encrypted = cipher_suite.encrypt(json_data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

# 解密函数
def decrypt_data(encrypted_str: str) -> dict:
    encrypted = base64.urlsafe_b64decode(encrypted_str.encode())
    decrypted = cipher_suite.decrypt(encrypted)
    return json.loads(decrypted.decode())

# 获取用户假名ID（基于浏览器指纹）
def get_pseudonym(request: Request) -> str:
    # 实际应用中应使用更复杂的方法生成假名
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else "127.0.0.1"
    fingerprint = f"{ip}-{user_agent}"
    return str(uuid.uuid5(uuid.NAMESPACE_OID, fingerprint))

# 生成健康图表（在客户端内存中处理）
def generate_chart(data: dict) -> str:
    # 使用matplotlib生成图表
    plt.figure(figsize=(10, 6))
    
    # 图表数据
    dates = [d['date'] for d in data.values() if 'date' in d]
    weights = [d['weight'] for d in data.values() if 'weight' in d]
    bmis = [d['weight'] / (d['height']/100)**2 for d in data.values() 
             if 'weight' in d and 'height' in d]
    
    # 创建图表
    plt.subplot(2, 1, 1)
    plt.plot(dates, weights, 'o-')
    plt.title('体重变化趋势')
    plt.ylabel('体重 (kg)')
    
    plt.subplot(2, 1, 2)
    plt.plot(dates, bmis, 's-')
    plt.title('BMI变化趋势')
    plt.ylabel('BMI')
    
    # 转换为Base64图片
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# 健康评分计算
def calculate_health_score(data: HealthData) -> int:
    score = 0
    
    # BMI评分 (18.5-24为健康范围)
    bmi = data.weight / ((data.height/100) ** 2)
    if 18.5 <= bmi <= 24:
        score += 30
    elif 17 <= bmi < 18.5 or 24 < bmi <= 27:
        score += 20
    else:
        score += 10
    
    # 睡眠评分 (7-9小时为最佳)
    if 7 <= data.sleep_hours <= 9:
        score += 25
    elif 6 <= data.sleep_hours < 7 or 9 < data.sleep_hours <= 10:
        score += 15
    else:
        score += 5
    
    # 运动评分
    if data.exercise_minutes >= 30:
        score += 25
    elif 15 <= data.exercise_minutes < 30:
        score += 15
    else:
        score += 5
    
    # 饮食评分
    score += data.diet_quality * 5
    
    # 心情评分
    score += data.mood * 5
    
    return min(score, 100)

# 路由处理
@app.get("/", response_class=HTMLResponse) #response_class=HTMLResponse:指定返回HTML内容
async def home(request: Request, pseudonym: str = Depends(get_pseudonym)):
    # 获取用户数据（如果存在）
    user_data = {}
    if pseudonym in health_db:
        encrypted_data = health_db[pseudonym]
        user_data = decrypt_data(encrypted_data)
    
    # 生成图表（如果需要）
    chart_img = None
    if user_data and len(user_data) > 1:
        chart_img = generate_chart(user_data)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user_data": user_data,
        "chart_img": chart_img,
        "pseudonym": pseudonym
    })

@app.post("/add-data")
async def add_health_data(
    request: Request,
    height: float = Form(...),
    weight: float = Form(...),
    sleep_hours: float = Form(...),
    exercise_minutes: int = Form(...),
    mood: int = Form(...),
    diet_quality: int = Form(...),
    pseudonym: str = Depends(get_pseudonym)
):
    # 创建健康数据对象
    data = HealthData(
        height=height,
        weight=weight,
        sleep_hours=sleep_hours,
        exercise_minutes=exercise_minutes,
        mood=mood,
        diet_quality=diet_quality
    )
    
    # 计算健康评分
    score = calculate_health_score(data)
    
    # 获取现有数据
    existing_data = {}
    if pseudonym in health_db:
        encrypted_data = health_db[pseudonym]
        existing_data = decrypt_data(encrypted_data)
    
    # 添加新记录
    record_id = str(uuid.uuid4())
    record = data.model_dump()
    record["score"] = score
    existing_data[record_id] = record
    
    # 加密并存储
    encrypted_data = encrypt_data(existing_data)
    health_db[pseudonym] = encrypted_data
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-data")
async def delete_health_data(
    request: Request,
    record_id: str = Form(...),
    pseudonym: str = Depends(get_pseudonym)
):
    if pseudonym in health_db:
        encrypted_data = health_db[pseudonym]
        existing_data = decrypt_data(encrypted_data)
        
        if record_id in existing_data:
            del existing_data[record_id]
            
            # 更新存储
            if existing_data:
                encrypted_data = encrypt_data(existing_data)
                health_db[pseudonym] = encrypted_data
            else:
                del health_db[pseudonym]
    
    return RedirectResponse(url="/", status_code=303)

@app.post("/reset-all")
async def reset_all_data(
    request: Request,
    pseudonym: str = Depends(get_pseudonym)
):
    if pseudonym in health_db:
        del health_db[pseudonym]
    return RedirectResponse(url="/", status_code=303)