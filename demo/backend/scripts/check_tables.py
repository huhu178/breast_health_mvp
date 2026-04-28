"""
检查数据库表结构脚本
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from load_env import load_environment
load_environment()

from sqlalchemy import create_engine, inspect
from config import Config

def check_database_tables():
    """检查数据库中的表"""
    print("=" * 60)
    print("🔍 正在连接数据库...")
    print("=" * 60)
    
    # 创建数据库引擎
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    inspector = inspect(engine)
    
    # 获取所有表名
    tables = inspector.get_table_names(schema='public')
    
    print(f"\n✅ 数据库连接成功！")
    print(f"📊 数据库: {Config.SQLALCHEMY_DATABASE_URI.split('@')[1]}")
    print(f"📋 共找到 {len(tables)} 张表\n")
    
    # 重点检查 C 端表
    c_tables = [t for t in tables if t.startswith('c_')]
    
    if c_tables:
        print("=" * 60)
        print("🎯 C端相关表 (c_*):")
        print("=" * 60)
        for table in sorted(c_tables):
            print(f"  ✓ {table}")
            
            # 获取表的列信息
            columns = inspector.get_columns(table, schema='public')
            print(f"    字段数: {len(columns)}")
            print(f"    主要字段: {', '.join([col['name'] for col in columns[:5]])}...")
            print()
    else:
        print("⚠️ 未找到 C端相关表 (c_*)")
        print("💡 可能需要运行建表脚本")
    
    # 检查 B 端表
    b_tables = [t for t in tables if t.startswith('b_')]
    
    if b_tables:
        print("=" * 60)
        print("🏢 B端相关表 (b_*):")
        print("=" * 60)
        for table in sorted(b_tables):
            print(f"  ✓ {table}")
        print()
    
    # 列出所有表
    print("=" * 60)
    print("📋 所有表列表:")
    print("=" * 60)
    for table in sorted(tables):
        row_count = engine.execute(f"SELECT COUNT(*) FROM public.{table}").scalar()
        print(f"  • {table:<30} ({row_count} 条记录)")
    
    print("\n" + "=" * 60)
    print("✅ 检查完成！")
    print("=" * 60)

if __name__ == '__main__':
    try:
        check_database_tables()
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

