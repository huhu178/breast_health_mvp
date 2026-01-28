#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新旧的 CHealthRecord 数据：从 CReport 的 report_html 中提取信息，或从 CPatient 中获取基本信息

注意：这个脚本只能更新基本信息（age, gender），其他字段需要重新提交问卷
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
from models import db, CPatient, CHealthRecord

def update_old_records():
    """更新旧的 CHealthRecord，从关联的 CPatient 中获取基本信息"""
    with app.app_context():
        try:
            print("开始更新旧的 CHealthRecord 数据...")
            
            # 查找所有 CHealthRecord
            records = CHealthRecord.query.all()
            updated_count = 0
            
            for record in records:
                # 获取关联的患者
                patient = CPatient.query.get(record.patient_id)
                if not patient:
                    continue
                
                # 如果记录的 age 为空，但患者有 age，则更新
                needs_update = False
                if record.age is None and patient.age:
                    record.age = patient.age
                    needs_update = True
                    print(f"  更新档案 {record.record_code}: age = {patient.age}")
                
                # 如果记录的 phone 为空，但患者有 phone，则更新
                if not record.phone and patient.phone:
                    record.phone = patient.phone
                    needs_update = True
                    print(f"  更新档案 {record.record_code}: phone = {patient.phone}")
                
                if needs_update:
                    updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                print(f"\n[OK] 已更新 {updated_count} 条记录")
            else:
                print("\n[INFO] 没有需要更新的记录")
            
            print("\n[OK] 更新完成！")
            print("\n注意：height, weight, diabetes_history, gaofang_address 等字段")
            print("需要用户重新提交问卷才能填充。")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] 更新失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    update_old_records()

