#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医院场景字段迁移脚本

使用方法：
    cd /root/20260402/breast_health_mvp/demo/backend
    python3 scripts/add_hospital_scene_fields.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db
from sqlalchemy import text


def run_migration():
    with app.app_context():
        try:
            print("开始执行医院场景字段迁移...")

            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS departments (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    code VARCHAR(50) UNIQUE,
                    hospital_name VARCHAR(150),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("[OK] departments 表已准备")

            db.session.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS department_id INTEGER
            """))
            db.session.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = 'users_department_id_fkey'
                    ) THEN
                        ALTER TABLE users
                            ADD CONSTRAINT users_department_id_fkey
                            FOREIGN KEY (department_id) REFERENCES departments(id);
                    END IF;
                END $$;
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_users_department_id ON users(department_id)
            """))
            print("[OK] users.department_id 已准备")

            db.session.execute(text("""
                ALTER TABLE b_patients
                ADD COLUMN IF NOT EXISTS department_id INTEGER,
                ADD COLUMN IF NOT EXISTS primary_doctor_id INTEGER
            """))
            db.session.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = 'b_patients_department_id_fkey'
                    ) THEN
                        ALTER TABLE b_patients
                            ADD CONSTRAINT b_patients_department_id_fkey
                            FOREIGN KEY (department_id) REFERENCES departments(id);
                    END IF;
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint WHERE conname = 'b_patients_primary_doctor_id_fkey'
                    ) THEN
                        ALTER TABLE b_patients
                            ADD CONSTRAINT b_patients_primary_doctor_id_fkey
                            FOREIGN KEY (primary_doctor_id) REFERENCES users(id);
                    END IF;
                END $$;
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_b_patients_department_id ON b_patients(department_id)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_b_patients_primary_doctor_id ON b_patients(primary_doctor_id)
            """))
            print("[OK] b_patients 医院场景字段已准备")

            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS b_report_followup_advices (
                    id SERIAL PRIMARY KEY,
                    patient_id INTEGER NOT NULL REFERENCES b_patients(id),
                    report_id INTEGER NOT NULL REFERENCES b_reports(id),
                    doctor_id INTEGER NOT NULL REFERENCES users(id),
                    advice_content TEXT,
                    suggested_next_followup_at DATE,
                    status VARCHAR(20) DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_report_followup_advices_patient_id
                ON b_report_followup_advices(patient_id)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_report_followup_advices_report_id
                ON b_report_followup_advices(report_id)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_report_followup_advices_doctor_id
                ON b_report_followup_advices(doctor_id)
            """))
            db.session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_report_followup_advices_status
                ON b_report_followup_advices(status)
            """))
            print("[OK] b_report_followup_advices 表已准备")

            db.session.commit()
            print("[OK] 医院场景字段迁移完成")
        except Exception as exc:
            db.session.rollback()
            print(f"[ERROR] 医院场景字段迁移失败: {exc}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    run_migration()
