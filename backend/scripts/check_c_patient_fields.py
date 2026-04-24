#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 c_patients 和 c_health_records 表的字段
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

def check_fields():
    """检查表字段"""
    with app.app_context():
        try:
            print("检查 c_patients 表字段...")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'c_patients' 
                ORDER BY ordinal_position
            """))
            print("\nc_patients 表的字段:")
            for row in result:
                print(f"  - {row[0]} ({row[1]}, nullable: {row[2]})")
            
            # 检查关键字段是否存在
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'c_patients' 
                AND column_name IN ('age', 'gender', 'nodule_type')
            """))
            c_patient_fields = [row[0] for row in result]
            print(f"\nc_patients 表的关键字段检查:")
            print(f"  age: {'存在' if 'age' in c_patient_fields else '不存在'}")
            print(f"  gender: {'存在' if 'gender' in c_patient_fields else '不存在'}")
            print(f"  nodule_type: {'存在' if 'nodule_type' in c_patient_fields else '不存在'}")
            
            print("\n" + "="*60)
            print("检查 c_health_records 表字段...")
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'c_health_records' 
                ORDER BY ordinal_position
            """))
            print("\nc_health_records 表的字段:")
            for row in result:
                print(f"  - {row[0]} ({row[1]}, nullable: {row[2]})")
            
            # 检查关键字段是否存在
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'c_health_records' 
                AND column_name IN ('height', 'weight', 'phone', 'diabetes_history', 'gaofang_address')
            """))
            c_record_fields = [row[0] for row in result]
            print(f"\nc_health_records 表的关键字段检查:")
            print(f"  height: {'存在' if 'height' in c_record_fields else '不存在'}")
            print(f"  weight: {'存在' if 'weight' in c_record_fields else '不存在'}")
            print(f"  phone: {'存在' if 'phone' in c_record_fields else '不存在'}")
            print(f"  diabetes_history: {'存在' if 'diabetes_history' in c_record_fields else '不存在'}")
            print(f"  gaofang_address: {'存在' if 'gaofang_address' in c_record_fields else '不存在'}")
            
            # 如果字段不存在，提示执行迁移
            missing_c_patient = [f for f in ['age', 'gender', 'nodule_type'] if f not in c_patient_fields]
            missing_c_record = [f for f in ['height', 'weight', 'phone', 'diabetes_history', 'gaofang_address'] if f not in c_record_fields]
            
            if missing_c_patient or missing_c_record:
                print("\n" + "="*60)
                print("[WARNING] 发现缺失的字段！")
                if missing_c_patient:
                    print(f"c_patients 表缺失字段: {', '.join(missing_c_patient)}")
                if missing_c_record:
                    print(f"c_health_records 表缺失字段: {', '.join(missing_c_record)}")
                print("\n请执行以下命令添加缺失的字段:")
                print("  python scripts/add_c_patient_fields.py")
            else:
                print("\n[OK] 所有字段都存在！")
            
        except Exception as e:
            print(f"\n[ERROR] 检查失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    check_fields()

