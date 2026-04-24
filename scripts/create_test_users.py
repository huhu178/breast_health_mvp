#!/usr/bin/env python3
"""
创建测试用户脚本
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models_separated import db, User, BPatient, CPatient
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_users():
    """创建测试用户"""
    print("👥 开始创建测试用户...")
    
    app = create_app()
    
    with app.app_context():
        # 检查是否已有用户
        existing_users = User.query.count()
        if existing_users > 0:
            print(f"⚠️ 系统中已有 {existing_users} 个用户，是否继续？(y/n)")
            choice = input().lower()
            if choice != 'y':
                print("❌ 取消创建")
                return False
        
        # 创建B端管理师用户
        print("👨‍⚕️ 创建B端管理师用户...")
        
        manager_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'real_name': '系统管理员',
                'email': 'admin@example.com',
                'phone': '13800000001',
                'role': 'admin'
            },
            {
                'username': 'manager1',
                'password': 'manager123',
                'real_name': '张医生',
                'email': 'zhang@example.com',
                'phone': '13800000002',
                'role': 'health_manager'
            },
            {
                'username': 'manager2',
                'password': 'manager123',
                'real_name': '李医生',
                'email': 'li@example.com',
                'phone': '13800000003',
                'role': 'health_manager'
            }
        ]
        
        created_managers = []
        for user_data in manager_users:
            # 检查用户是否已存在
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"  ⚠️ 用户 {user_data['username']} 已存在，跳过")
                created_managers.append(existing_user)
                continue
            
            user = User(
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                real_name=user_data['real_name'],
                email=user_data['email'],
                phone=user_data['phone'],
                role=user_data['role'],
                is_active=True
            )
            db.session.add(user)
            created_managers.append(user)
            print(f"  ✅ 创建用户: {user_data['username']} ({user_data['real_name']})")
        
        db.session.commit()
        
        # 创建测试患者数据
        print("\n👤 创建测试患者数据...")
        
        # B端患者
        b_patients_data = [
            {
                'name': '王女士',
                'age': 35,
                'gender': '女',
                'phone': '13900000001',
                'wechat_id': 'wang_001',
                'manager_id': created_managers[1].id,  # 分配给张医生
                'source_channel': 'b_end',
                'status': 'active',
                'is_new': True
            },
            {
                'name': '刘女士',
                'age': 42,
                'gender': '女',
                'phone': '13900000002',
                'wechat_id': 'liu_002',
                'manager_id': created_managers[2].id,  # 分配给李医生
                'source_channel': 'b_end',
                'status': 'active',
                'is_new': False
            }
        ]
        
        for patient_data in b_patients_data:
            patient_code = f"BP{datetime.now().strftime('%Y%m%d%H%M%S')}"
            b_patient = BPatient(
                patient_code=patient_code,
                name=patient_data['name'],
                age=patient_data['age'],
                gender=patient_data['gender'],
                phone=patient_data['phone'],
                wechat_id=patient_data['wechat_id'],
                manager_id=patient_data['manager_id'],
                source_channel=patient_data['source_channel'],
                status=patient_data['status'],
                is_new=patient_data['is_new']
            )
            db.session.add(b_patient)
            print(f"  ✅ 创建B端患者: {patient_data['name']}")
        
        # C端患者
        c_patients_data = [
            {
                'name': '陈女士',
                'phone': '13900000003',
                'wechat_id': 'chen_003',
                'source_channel': 'c_end',
                'status': 'active',
                'is_contacted': False
            },
            {
                'name': '赵女士',
                'phone': '13900000004',
                'wechat_id': 'zhao_004',
                'source_channel': 'c_end',
                'status': 'active',
                'is_contacted': True
            }
        ]
        
        for patient_data in c_patients_data:
            patient_code = f"CP{datetime.now().strftime('%Y%m%d%H%M%S')}"
            c_patient = CPatient(
                patient_code=patient_code,
                name=patient_data['name'],
                phone=patient_data['phone'],
                wechat_id=patient_data['wechat_id'],
                source_channel=patient_data['source_channel'],
                status=patient_data['status'],
                is_contacted=patient_data['is_contacted']
            )
            db.session.add(c_patient)
            print(f"  ✅ 创建C端患者: {patient_data['name']}")
        
        db.session.commit()
        
        # 统计结果
        manager_count = User.query.count()
        b_patient_count = BPatient.query.count()
        c_patient_count = CPatient.query.count()
        
        print(f"\n📊 创建结果统计:")
        print(f"  - B端管理师: {manager_count} 个")
        print(f"  - B端患者: {b_patient_count} 个")
        print(f"  - C端患者: {c_patient_count} 个")
        
        print(f"\n🔑 测试账号信息:")
        print(f"  - 管理员: admin / admin123")
        print(f"  - 张医生: manager1 / manager123")
        print(f"  - 李医生: manager2 / manager123")
        
        return True

def main():
    """主函数"""
    print("🚀 开始创建测试用户...")
    print("=" * 50)
    
    try:
        success = create_test_users()
        if success:
            print("\n✅ 测试用户创建完成!")
        else:
            print("\n❌ 测试用户创建失败!")
            return False
    except Exception as e:
        print(f"\n❌ 创建过程中出错: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
