"""
测试数据库连接
"""
import sys
import os

# 添加 backend 路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from load_env import load_environment
load_environment()

from config import Config
from sqlalchemy import create_engine, text

def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("正在测试数据库连接...")
    print("=" * 60)

    # 打印配置（隐藏密码）
    db_url = Config.SQLALCHEMY_DATABASE_URI
    # 隐藏密码显示
    safe_url = db_url.split('@')[0].split(':')[:-1]
    safe_url = ':'.join(safe_url) + ':****@' + db_url.split('@')[1]
    print(f"\n数据库地址: {safe_url}\n")

    try:
        # 创建引擎
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("✅ 数据库连接成功！")
            print(f"PostgreSQL 版本: {version}\n")

            # 查询当前数据库
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"当前数据库: {db_name}")

            # 查询数据库中的表
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()
            print(f"\n数据库中的表 ({len(tables)} 个):")
            for table in tables:
                print(f"  - {table[0]}")

        print("\n" + "=" * 60)
        print("✅ 测试完成！数据库连接正常！")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 数据库连接失败！")
        print(f"错误信息: {str(e)}\n")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_connection()
