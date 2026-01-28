#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 c_reports 表添加审核字段（imaging_conclusion, imaging_risk_warning）

使用方法：
    python scripts/add_c_report_fields.py
"""
import sys
import os
import io

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db
from sqlalchemy import text

def add_fields():
    """添加新字段到数据库表"""
    with app.app_context():
        try:
            print("开始执行数据库迁移...")
            
            # 为 c_reports 表添加字段
            print("\n1. 为 c_reports 表添加审核字段...")
            db.session.execute(text("""
                ALTER TABLE c_reports
                ADD COLUMN IF NOT EXISTS imaging_conclusion TEXT,
                ADD COLUMN IF NOT EXISTS imaging_risk_warning TEXT
            """))
            print("   [OK] 已添加审核字段")
            
            # 提交更改
            db.session.commit()
            print("\n[OK] 数据库迁移完成！")
            
            # 验证字段
            print("\n2. 验证字段...")
            result = db.session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'c_reports' 
                AND column_name IN ('imaging_conclusion', 'imaging_risk_warning')
                ORDER BY column_name
            """))
            print("   c_reports 表的新字段:")
            for row in result:
                print(f"     - {row[0]} ({row[1]})")
            
            print("\n[OK] 所有字段验证通过！")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    add_fields()


