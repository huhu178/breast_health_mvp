"""
更新 C 端数据表（添加缺失字段）
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from load_env import load_environment
load_environment()

from sqlalchemy import create_engine, text
from config import Config

def update_c_tables():
    """添加缺失的字段"""
    print("=" * 60)
    print("🔧 开始更新 C 端数据表...")
    print("=" * 60)
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    sql_script = """
    -- 为 c_conversations 表添加缺失的字段
    ALTER TABLE public.c_conversations 
    ADD COLUMN IF NOT EXISTS collected_data JSONB;
    
    ALTER TABLE public.c_conversations 
    ADD COLUMN IF NOT EXISTS summary TEXT;
    
    ALTER TABLE public.c_conversations 
    ADD COLUMN IF NOT EXISTS keywords TEXT;
    
    -- 为 c_messages 表添加缺失的字段
    ALTER TABLE public.c_messages 
    ADD COLUMN IF NOT EXISTS extra_data JSONB;
    """
    
    print("\n📝 执行 SQL 更新...\n")
    
    try:
        with engine.connect() as conn:
            conn.execute(text(sql_script))
            conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ C 端数据表更新成功！")
        print("=" * 60)
        print("\n添加的字段:")
        print("  ✓ c_conversations.collected_data (JSONB)")
        print("  ✓ c_conversations.summary (TEXT)")
        print("  ✓ c_conversations.keywords (TEXT)")
        print("  ✓ c_messages.extra_data (JSONB)")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    update_c_tables()

