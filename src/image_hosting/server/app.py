from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from image_hosting.config.settings import Config

# 创建 FastAPI 应用
app = FastAPI(
    title="ImageDoge API",
    description="ImageDoge static file server",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount(
    "/static",
    StaticFiles(directory=str(Config.ROOT_DIR / "static")),
    name="static"
)

@app.get("/")
async def root():
    """健康检查接口"""
    return {"status": "ok", "service": "ImageDoge static file server"} 