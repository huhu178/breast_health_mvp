#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查最新的 CHealthRecord 数据，看看字段值是否正确保存
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
from models import db, CHealthRecord, CPatient
from sqlalchemy import text

def check_latest_record():
    """检查最新的记录"""
    with app.app_context():
        try:
            print("检查最新的 CHealthRecord 数据...")
            
            # 查找最新的记录
            latest_record = CHealthRecord.query.order_by(CHealthRecord.created_at.desc()).first()
            if not latest_record:
                print("[INFO] 没有找到 CHealthRecord 记录")
                return
            
            print(f"\n最新记录: {latest_record.record_code}")
            print(f"创建时间: {latest_record.created_at}")
            
            # 检查关键字段
            print(f"\n关键字段值:")
            print(f"  age: {latest_record.age}")
            print(f"  height: {latest_record.height}")
            print(f"  weight: {latest_record.weight}")
            print(f"  phone: {latest_record.phone}")
            print(f"  diabetes_history: {latest_record.diabetes_history}")
            print(f"  gaofang_address: {latest_record.gaofang_address}")
            
            # 检查患者信息
            patient = CPatient.query.get(latest_record.patient_id)
            if patient:
                print(f"\n关联患者信息:")
                print(f"  患者编号: {patient.patient_code}")
                print(f"  姓名: {patient.name}")
                print(f"  年龄: {patient.age}")
                print(f"  性别: {patient.gender}")
                print(f"  结节类型: {patient.nodule_type}")
            
            # 检查最近5条记录
            print(f"\n最近5条记录的关键字段:")
            recent_records = CHealthRecord.query.order_by(CHealthRecord.created_at.desc()).limit(5).all()
            for i, record in enumerate(recent_records, 1):
                print(f"\n{i}. {record.record_code} (创建于: {record.created_at})")
                print(f"   age: {record.age}, height: {record.height}, weight: {record.weight}")
                print(f"   phone: {record.phone}, diabetes_history: {record.diabetes_history}")
            
        except Exception as e:
            print(f"\n[ERROR] 检查失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    check_latest_record()

