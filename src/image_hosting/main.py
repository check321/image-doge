import os
import uvicorn
from multiprocessing import Process
from image_hosting.config.settings import Config
from image_hosting.ui.app import ImageHostingUI
from image_hosting.server.app import app as fastapi_app

def run_fastapi():
    """运行 FastAPI 服务"""
    uvicorn.run(
        fastapi_app,
        host=Config.HOST,
        port=Config.STATIC_PORT,
        log_level="info" if Config.DEBUG else "error"
    )

def run_gradio():
    """运行 Gradio 服务"""
    ui = ImageHostingUI()
    demo = ui.create_ui()
    demo.launch(
        server_name=Config.HOST,
        server_port=Config.PORT,
        debug=Config.DEBUG,
    )

def main():
    # 确保配置是最新的
    Config.load_config()
    
    # 启动 FastAPI 进程
    fastapi_process = Process(target=run_fastapi)
    fastapi_process.start()
    
    try:
        # 运行 Gradio 服务（主进程）
        run_gradio()
    finally:
        # 确保在主程序退出时关闭 FastAPI 进程
        fastapi_process.terminate()
        fastapi_process.join()

if __name__ == "__main__":
    main() 