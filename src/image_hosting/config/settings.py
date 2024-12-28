import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent.parent.absolute()

# 加载 .env 文件
env_path = os.path.join(ROOT_DIR, '.env')
load_dotenv(env_path)

class Config:
    # 服务配置
    HOST = os.getenv("IMAGE_HOST", "0.0.0.0")
    PORT = int(os.getenv("IMAGE_PORT", "7860"))
    DEBUG = os.getenv("IMAGE_DEBUG", "False").lower() == "true"
    
    # 存储配置
    STORAGE = {
        "LOCAL": {
            # 上传文件存储根目录
            "root_dir": ROOT_DIR,
            # 上传文件存储子目录（从环境变量读取）
            "upload_dir": os.getenv("IMAGE_UPLOAD_DIR", "static/uploads"),
            # 文件访问URL前缀
            "url_prefix": os.getenv(
                "IMAGE_URL_PREFIX", 
                os.getenv("IMAGE_SERVER_URL", f"http://localhost:{PORT}")
            ),
            # 文件访问路径前缀（从环境变量读取）
            "path_prefix": os.getenv("IMAGE_PATH_PREFIX", "static/uploads")
        }
    }
    
    # 当前使用的存储配置
    CURRENT_STORAGE = "LOCAL"
    
    @classmethod
    def get_storage_config(cls) -> Dict[str, str]:
        """获取当前存储配置"""
        storage_config = cls.STORAGE[cls.CURRENT_STORAGE]
        
        # 构建完整的上传目录路径
        upload_path = os.path.join(
            storage_config["root_dir"],
            storage_config["upload_dir"]
        )
        
        return {
            "upload_dir": upload_path,
            "url_prefix": storage_config["url_prefix"],
            "path_prefix": storage_config["path_prefix"]
        }
    
    # 上传限制
    MAX_FILE_SIZE = int(os.getenv("IMAGE_MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 创建上传目录
storage_config = Config.get_storage_config()
os.makedirs(storage_config["upload_dir"], exist_ok=True) 