"""
修复 c_reports 表结构（将 lead_id 重命名为 patient_id，并添加缺失字段）
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from load_env import load_environment
load_environment()

from sqlalchemy import create_engine, text
from config import Config

def fix_c_reports_table():
    """修复 c_reports 表结构"""
    print("=" * 60)
    print("🔧 开始修复 c_reports 表结构...")
    print("=" * 60)
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    sql_script = """
    -- 检查表是否存在
    DO $$
    BEGIN
        -- 如果 lead_id 字段存在，重命名为 patient_id
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='c_reports' 
            AND column_name='lead_id'
        ) THEN
            ALTER TABLE public.c_reports RENAME COLUMN lead_id TO patient_id;
            RAISE NOTICE 'lead_id 已重命名为 patient_id';
        END IF;
        
        -- 添加缺失的字段（如果不存在）
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='c_reports' 
            AND column_name='report_summary'
        ) THEN
            ALTER TABLE public.c_reports ADD COLUMN report_summary TEXT;
            RAISE NOTICE '已添加 report_summary 字段';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='c_reports' 
            AND column_name='risk_level'
        ) THEN
            ALTER TABLE public.c_reports ADD COLUMN risk_level VARCHAR(20);
            RAISE NOTICE '已添加 risk_level 字段';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='c_reports' 
            AND column_name='report_type'
        ) THEN
            ALTER TABLE public.c_reports ADD COLUMN report_type VARCHAR(20) DEFAULT 'patient_friendly';
            RAISE NOTICE '已添加 report_type 字段';
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='c_reports' 
            AND column_name='access_level'
        ) THEN
            ALTER TABLE public.c_reports ADD COLUMN access_level VARCHAR(20) DEFAULT 'c_accessible';
            RAISE NOTICE '已添加 access_level 字段';
        END IF;
        
        -- 修改 patient_id 为可空（允许匿名用户）
        ALTER TABLE public.c_reports ALTER COLUMN patient_id DROP NOT NULL;
        RAISE NOTICE 'patient_id 已修改为可空';
        
    END $$;
    
    -- 显示当前表结构
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name='c_reports'
    ORDER BY ordinal_position;
    """
    
    print("\n📝 执行 SQL 更新...\n")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_script))
            conn.commit()
            
            # 显示表结构
            print("\n当前 c_reports 表结构:")
            print("-" * 60)
            for row in result:
                print(f"  {row[0]:25} {row[1]:20} nullable={row[2]}")
        
        print("\n" + "=" * 60)
        print("✅ c_reports 表结构修复成功！")
        print("=" * 60)
        print("\n修复内容:")
        print("  ✓ lead_id → patient_id (重命名)")
        print("  ✓ patient_id 允许为 NULL (匿名用户)")
        print("  ✓ 添加缺失字段: report_summary, risk_level, report_type, access_level")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_c_reports_table()

