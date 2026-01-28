"""
文件上传工具函数
处理文件保存、路径管理等
"""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


class FileUploadManager:
    """文件上传管理器"""
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # 文件大小限制（10MB）
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUploadManager.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """获取文件类型"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext == 'pdf':
            return 'pdf'
        elif ext in ['doc', 'docx']:
            return 'word'
        elif ext in ['jpg', 'jpeg', 'png']:
            return 'image'
        return 'unknown'
    
    @staticmethod
    def generate_file_path(record_id: int, filename: str) -> tuple:
        """
        生成文件存储路径
        
        Args:
            record_id: 健康档案ID
            filename: 原始文件名
            
        Returns:
            tuple: (文件路径, 文件名)
        """
        # 生成唯一文件名
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # 按日期组织目录结构：uploads/reports/YYYY/MM/record_id/
        now = datetime.now()
        date_path = now.strftime('%Y/%m')
        file_dir = os.path.join('uploads', 'reports', date_path, str(record_id))
        
        # 确保目录存在
        os.makedirs(file_dir, exist_ok=True)
        
        # 完整文件路径
        file_path = os.path.join(file_dir, unique_filename)
        
        return file_path, unique_filename
    
    @staticmethod
    def save_file(file, record_id: int) -> tuple:
        """
        保存上传的文件
        
        Args:
            file: Flask上传的文件对象
            record_id: 健康档案ID
            
        Returns:
            tuple: (文件路径, 文件名, 文件大小) 或 (None, None, None) 如果失败
        """
        try:
            # 检查文件
            if not file or not file.filename:
                print("❌ 文件对象无效")
                return None, None, None
            
            # 检查文件扩展名
            if not FileUploadManager.is_allowed_file(file.filename):
                print(f"❌ 不支持的文件类型: {file.filename}")
                return None, None, None
            
            # 检查文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > FileUploadManager.MAX_FILE_SIZE:
                print(f"❌ 文件大小超过限制: {file_size} bytes")
                return None, None, None
            
            # 生成文件路径
            file_path, unique_filename = FileUploadManager.generate_file_path(record_id, file.filename)
            
            # 保存文件
            file.save(file_path)
            
            print(f"✅ 文件保存成功: {file_path} ({file_size} bytes)")
            return file_path, file.filename, file_size
            
        except Exception as e:
            print(f"❌ 保存文件失败: {str(e)}")
            return None, None, None
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ 文件删除成功: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ 删除文件失败: {str(e)}")
            return False


# 创建单例
file_upload_manager = FileUploadManager()




