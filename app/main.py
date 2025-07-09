
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
# /static：这是URL路径前缀，表示所有以/static开头的请求都会被交给StaticFiles处理。
# StaticFiles(directory="static")：指定静态文件存放的目录为static。也就是说，static文件夹中的所有文件都可以通过/static路径来访问。
# name="static"：为挂载的静态文件设置一个名称，可以方便地引用。


