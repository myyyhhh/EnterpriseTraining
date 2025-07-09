from fastapi import FastAPI, Request, Form, Depends


from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
# /static：这是URL路径前缀，表示所有以/static开头的请求都会被交给StaticFiles处理。
# StaticFiles(directory="static")：指定静态文件存放的目录为static。也就是说，static文件夹中的所有文件都可以通过/static路径来访问。
# name="static"：为挂载的静态文件设置一个名称，可以方便地引用。

templates = Jinja2Templates(directory="templates")
# /templates：这是模板文件存放的目录，FastAPI会在这个目录下查找HTML模板文件。


# 数据类
class Templates(BaseModel):


    request: Request


#图表类
class ChartImage(BaseModel):
    image: str


@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):


    # 画图表
    if True:
        # 这里可以添加生成图表的逻辑
        pass

    return templates.TemplateResponse(
        "index.html", # template/index.html
        {
            "request": request
        },
    )