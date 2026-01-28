"""
数据库迁移管理脚本
使用方法:
    flask db init       # 初始化迁移目录（只需执行一次）
    flask db migrate -m "描述"  # 生成迁移脚本
    flask db upgrade    # 执行迁移
    flask db downgrade  # 回滚迁移

注意：需要设置环境变量 FLASK_APP=manage.py
或使用: export FLASK_APP=manage.py (Linux/Mac) 或 set FLASK_APP=manage.py (Windows)
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
