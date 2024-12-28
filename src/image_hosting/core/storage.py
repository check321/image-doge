import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from image_hosting.config.settings import Config

class StorageError(Exception):
    """存储相关异常"""
    pass

class ImageStorage:
    def __init__(self):
        self.storage_config = Config.get_storage_config()
    
    def validate_file(self, filepath: str) -> bool:
        """验证文件"""
        if not filepath:
            return False
        
        ext = Path(filepath).suffix.lower()
        if ext not in Config.ALLOWED_EXTENSIONS:
            return False
            
        return True

    def save_image(self, filepath: str) -> Optional[str]:
        """保存图片并返回URL"""
        if not self.validate_file(filepath):
            raise StorageError("无效的文件类型")

        try:
            ext = Path(filepath).suffix
            filename = f"{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}{ext}"
            save_path = os.path.join(self.storage_config["upload_dir"], filename)
            
            shutil.copy2(filepath, save_path)
            
            # 构建访问URL
            url_path = f"{self.storage_config['path_prefix']}/{filename}"
            return f"{self.storage_config['url_prefix']}/{url_path}"
        except Exception as e:
            raise StorageError(f"文件保存失败: {str(e)}")
    
    def get_image_list(self) -> List[Dict[str, str]]:
        """获取已上传的图片列表"""
        try:
            images = []
            for filename in os.listdir(self.storage_config["upload_dir"]):
                if Path(filename).suffix.lower() in Config.ALLOWED_EXTENSIONS:
                    # 构建访问URL
                    url_path = f"{self.storage_config['path_prefix']}/{filename}"
                    url = f"{self.storage_config['url_prefix']}/{url_path}"
                    
                    file_path = os.path.join(self.storage_config["upload_dir"], filename)
                    images.append({
                        "filename": filename,
                        "url": url,
                        "upload_time": datetime.fromtimestamp(
                            os.path.getctime(file_path)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })
            # 按上传时间倒序排序
            return sorted(images, key=lambda x: x["upload_time"], reverse=True)
        except Exception as e:
            raise StorageError(f"获取图片列表失败: {str(e)}") 