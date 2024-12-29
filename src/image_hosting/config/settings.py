import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv, find_dotenv

class Config:
    @classmethod
    def load_config(cls):
        """加载配置"""
        # 获取项目根目录
        cls.ROOT_DIR = Path(__file__).parent.parent.parent.parent.absolute()
        
        # 加载 .env 文件，override=True 确保重新加载
        env_path = os.path.join(cls.ROOT_DIR, '.env')
        load_dotenv(env_path, override=True)
        
        # 服务配置
        cls.HOST = os.getenv("IMAGE_HOST", "0.0.0.0")
        cls.PORT = int(os.getenv("IMAGE_PORT", "7860"))
        cls.DEBUG = os.getenv("IMAGE_DEBUG", "False").lower() == "true"
        
        # 静态文件服务配置
        cls.STATIC_PORT = int(os.getenv("IMAGE_STATIC_PORT", "8000"))
        
        # 存储配置
        cls.STORAGE = {
            "LOCAL": {
                # 上传文件存储根目录
                "root_dir": cls.ROOT_DIR,
                # 上传文件存储子目录（从环境变量读取）
                "upload_dir": os.getenv("IMAGE_UPLOAD_DIR", "static/uploads"),
                # 文件访问URL前缀（使用静态文件服务地址）
                "url_prefix": os.getenv(
                    "IMAGE_URL_PREFIX", 
                    f"http://localhost:{cls.STATIC_PORT}"
                ),
                # 文件访问路径前缀
                "path_prefix": os.getenv("IMAGE_PATH_PREFIX", "static/uploads")
            }
        }
        
        # 当前使用的存储配置
        cls.CURRENT_STORAGE = "LOCAL"
        
        # 上传限制
        cls.MAX_FILE_SIZE = int(os.getenv("IMAGE_MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
        cls.ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        
        # 图片压缩配置
        cls.MAX_IMAGE_SIZE = int(os.getenv("IMAGE_MAX_SIZE", "1920"))  # 最大边长
        cls.COMPRESS_QUALITY = int(os.getenv("IMAGE_COMPRESS_QUALITY", "85"))  # JPEG压缩质量
    
    @classmethod
    def get_storage_config(cls) -> Dict[str, str]:
        """获取当前存储配置"""
        storage_config = cls.STORAGE[cls.CURRENT_STORAGE]
        
        # 构建完整的上传目录路径
        upload_path = os.path.join(
            storage_config["root_dir"],
            storage_config["upload_dir"]
        )
        
        # 修改 URL 构建逻辑，确保正确的路径分隔符
        path_prefix = storage_config["path_prefix"].replace('\\', '/')
        
        return {
            "upload_dir": upload_path,
            "url_prefix": storage_config["url_prefix"].rstrip('/'),  # 移除末尾的斜杠
            "path_prefix": path_prefix.strip('/')  # 移除首尾的斜杠
        }

# 初始化配置
Config.load_config()

# 创建上传目录
storage_config = Config.get_storage_config()
os.makedirs(storage_config["upload_dir"], exist_ok=True) 