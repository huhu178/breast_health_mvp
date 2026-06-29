#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医院场景默认数据初始化脚本。

用途：
1. 创建默认科室。
2. 创建医生、科室主任、医生助手测试账号。
3. 给现有用户绑定默认科室。
4. 给历史患者补齐所属科室、主要负责医生和空缺管理师。

脚本幂等，可重复执行。

使用方法：
    cd /root/20260402/breast_health_mvp/demo/backend
    python3 scripts/init_hospital_scene_data.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BPatient, Department, User, db
from werkzeug.security import generate_password_hash


HOSPITAL_NAME = '示例医院'

DEPARTMENTS = [
    {'name': '健康管理中心', 'code': 'HEALTH_MGMT', 'hospital_name': HOSPITAL_NAME},
    {'name': '乳腺科', 'code': 'BREAST', 'hospital_name': HOSPITAL_NAME},
    {'name': '甲状腺科', 'code': 'THYROID', 'hospital_name': HOSPITAL_NAME},
    {'name': '呼吸科', 'code': 'RESPIRATORY', 'hospital_name': HOSPITAL_NAME},
]

LEGACY_DEPARTMENT_ALIASES = {
    '乳腺外科': '乳腺科',
}

DEFAULT_USERS = [
    {
        'username': 'doctor_li',
        'password': 'Doctor@123456',
        'real_name': '李医生',
        'role': 'doctor',
        'phone': '13800001001',
        'department_code': 'BREAST',
    },
    {
        'username': 'director_breast',
        'password': 'Director@123456',
        'real_name': '乳腺科主任',
        'role': 'department_director',
        'phone': '13800001002',
        'department_code': 'BREAST',
    },
    {
        'username': 'assistant_chen',
        'password': 'Assistant@123456',
        'real_name': '陈助手',
        'role': 'doctor_assistant',
        'phone': '13800001003',
        'department_code': 'HEALTH_MGMT',
    },
    {
        'username': 'platform_admin',
        'password': 'Platform@123456',
        'real_name': '平台管理员',
        'role': 'system_admin',
        'phone': '13800001004',
        'department_code': 'HEALTH_MGMT',
    },
]


def get_or_create_department(department_data):
    dept = Department.query.filter_by(code=department_data['code']).first()
    if not dept:
        dept = Department.query.filter_by(name=department_data['name']).first()
    if not dept and department_data['name'] in LEGACY_DEPARTMENT_ALIASES.values():
        legacy_names = [old for old, new in LEGACY_DEPARTMENT_ALIASES.items() if new == department_data['name']]
        dept = Department.query.filter(Department.name.in_(legacy_names)).first() if legacy_names else None
    if not dept:
        dept = Department(**department_data, is_active=True)
        db.session.add(dept)
        db.session.flush()
        print(f"[CREATE] 科室：{dept.name}")
    else:
        changed = False
        for key, value in department_data.items():
            if getattr(dept, key) != value:
                setattr(dept, key, value)
                changed = True
        if changed:
            print(f"[UPDATE] 同步科室信息：{dept.name}")
        else:
            print(f"[SKIP] 科室已存在：{dept.name}")
    return dept


def get_or_create_departments():
    departments = {}
    for item in DEPARTMENTS:
        dept = get_or_create_department(item)
        departments[item['code']] = dept
    return departments


def get_or_create_user(user_data, departments):
    user = User.query.filter_by(username=user_data['username']).first()
    department_id = departments[user_data['department_code']].id
    if not user:
        user = User(
            username=user_data['username'],
            password_hash=generate_password_hash(user_data['password']),
            real_name=user_data['real_name'],
            phone=user_data['phone'],
            role=user_data['role'],
            department_id=department_id,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()
        print(f"[CREATE] 用户：{user.username} / {user.real_name} / {user.role}")
    else:
        changed = False
        if user.role != user_data['role']:
            user.role = user_data['role']
            changed = True
        if user.department_id != department_id:
            user.department_id = department_id
            changed = True
        if user.real_name != user_data['real_name']:
            user.real_name = user_data['real_name']
            changed = True
        if not user.phone:
            user.phone = user_data['phone']
            changed = True
        print(f"[{'UPDATE' if changed else 'SKIP'}] 用户：{user.username} / {user.role}")
    return user


def bind_existing_users(departments):
    health_management_department_id = departments['HEALTH_MGMT'].id
    count = 0
    for user in User.query.filter(User.role.in_(['health_manager', 'doctor_assistant'])).all():
        if user.department_id == health_management_department_id:
            continue
        user.department_id = health_management_department_id
        count += 1
    print(f"[UPDATE] 已给 {count} 个健康管理人员绑定健康管理中心")


def choose_default_manager():
    manager = User.query.filter_by(username='admin').first()
    if manager:
        return manager
    manager = User.query.filter(User.role.in_(['health_manager', 'doctor_assistant'])).order_by(User.id.asc()).first()
    if manager:
        return manager
    return User.query.order_by(User.id.asc()).first()


def patch_patients(department_id, doctor_id, manager_id):
    total = BPatient.query.count()
    patched_department = 0
    patched_doctor = 0
    patched_manager = 0

    for patient in BPatient.query.order_by(BPatient.id.asc()).all():
        if not patient.department_id:
            patient.department_id = department_id
            patched_department += 1
        if not patient.primary_doctor_id:
            patient.primary_doctor_id = doctor_id
            patched_doctor += 1
        if not patient.manager_id and manager_id:
            patient.manager_id = manager_id
            patched_manager += 1

    print(f"[UPDATE] 患者总数：{total}")
    print(f"[UPDATE] 补齐所属科室：{patched_department}")
    print(f"[UPDATE] 补齐主要负责医生：{patched_doctor}")
    print(f"[UPDATE] 补齐管理人员：{patched_manager}")


def init_data():
    with app.app_context():
        try:
            departments = get_or_create_departments()
            created_users = {
                data['role']: get_or_create_user(data, departments)
                for data in DEFAULT_USERS
            }
            bind_existing_users(departments)

            doctor = created_users['doctor']
            manager = choose_default_manager()
            patch_patients(departments['BREAST'].id, doctor.id, manager.id if manager else None)

            db.session.commit()
            print("\n[OK] 医院场景默认数据初始化完成")
            print("\n默认账号：")
            for data in DEFAULT_USERS:
                print(f"  - {data['username']} / {data['password']} / {data['real_name']} / {data['role']}")
        except Exception as exc:
            db.session.rollback()
            print(f"[ERROR] 初始化失败：{exc}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    init_data()
