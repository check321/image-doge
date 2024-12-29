import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PIL import Image
import io

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

    def save_image(self, filepath: str, compress: bool = False, quality: int = None) -> Tuple[str, Optional[Tuple[int, int]]]:
        """
        保存图片并返回URL
        
        Args:
            filepath: 图片文件路径
            compress: 是否压缩图片
            quality: 压缩质量(1-100)，None时使用配置默认值
            
        Returns:
            tuple: (图片URL, (原始大小, 压缩后大小)) 如果不压缩，则第二个元素为None
        """
        if not self.validate_file(filepath):
            raise StorageError("无效的文件类型")

        try:
            ext = Path(filepath).suffix.lower()
            filename = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join(self.storage_config["upload_dir"], filename)
            
            original_size = os.path.getsize(filepath)
            
            if compress:
                # 压缩图片
                compressed_size = self._compress_image(
                    filepath,
                    save_path,
                    quality or Config.COMPRESS_QUALITY
                )
                sizes = (original_size, compressed_size)
            else:
                # 直接复制文件
                shutil.copy2(filepath, save_path)
                sizes = None
            
            # 构建访问URL
            url_path = f"{self.storage_config['path_prefix']}/{filename}"
            return f"{self.storage_config['url_prefix']}/{url_path}", sizes
        except Exception as e:
            raise StorageError(f"文件保存失败: {str(e)}")
    
    def _compress_image(self, source_path: str, target_path: str, quality: int) -> int:
        """
        压缩图片
        
        Args:
            source_path: 源文件路径
            target_path: 目标文件路径
            quality: 压缩质量(1-100)
            
        Returns:
            int: 压缩后的文件大小
        """
        try:
            # 打开图片
            with Image.open(source_path) as img:
                # 转换为RGB模式（如果是RGBA）
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 计算新的尺寸（保持宽高比）
                max_size = Config.MAX_IMAGE_SIZE
                ratio = min(max_size/max(img.size[0], img.size[1]), 1.0)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                
                # 调整大小
                if ratio < 1.0:
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存压缩后的图片
                img.save(target_path, 'JPEG', quality=quality)
                
                return os.path.getsize(target_path)
        except Exception as e:
            raise StorageError(f"图片压缩失败: {str(e)}")
    
    def get_image_list(self) -> List[Dict[str, str]]:
        """获取已上传的图片列表"""
        try:
            images = []
            for filename in os.listdir(self.storage_config["upload_dir"]):
                if Path(filename).suffix.lower() in Config.ALLOWED_EXTENSIONS:
                    file_path = os.path.join(self.storage_config["upload_dir"], filename)
                    url_path = f"{self.storage_config['path_prefix']}/{filename}"
                    url = f"{self.storage_config['url_prefix']}/{url_path}"
                    
                    # 获取文件大小
                    size_bytes = os.path.getsize(file_path)
                    # 转换为人类可读的大小
                    size = self._format_size(size_bytes)
                    
                    images.append({
                        "filename": filename,
                        "url": url,
                        "size": size,
                        "size_bytes": size_bytes,  # 用于排序
                        "upload_time": datetime.fromtimestamp(
                            os.path.getctime(file_path)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })
            # 按上传时间倒序排序
            return sorted(images, key=lambda x: x["upload_time"], reverse=True)
        except Exception as e:
            raise StorageError(f"获取图片列表失败: {str(e)}")
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """将字节大小转换为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB" 