"""
数据库表结构更新脚本
用于删除旧表并重建新表结构
"""
import sys
import os
# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from models import db

def update_database():
    """更新数据库表结构"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  警告：即将删除 health_records_mvp 表并重建")
        print("   这将清空所有档案数据（患者数据不受影响）")
        
        try:
            # 删除旧表
            print("\n📋 删除旧的档案表...")
            db.session.execute(db.text("DROP TABLE IF EXISTS health_records_mvp CASCADE"))
            db.session.commit()
            print("✅ 旧表已删除")
            
            # 重建表
            print("\n🔨 创建新的档案表...")
            db.create_all()
            print("✅ 新表创建成功！")
            
            print("\n🎉 数据库更新完成！")
            print("\n📊 新表包含以下字段：")
            print("   - 基本信息：age, birads_level, family_history")
            print("   - 病程信息：nodule_discovery_time, course_stage, tnm_stage (新增)")
            print("   - 症状信息：symptoms, pain_level, pain_type, nipple_discharge_type, skin_change_type (扩展)")
            print("   - 影像学：nodule_location, nodule_size, boundary_features, internal_echo, blood_flow_signal, elasticity_score")
            print("   - 生物节律：rhythm_type, cycle_phase, sleep_quality, sleep_condition (扩展)")
            print("   - 检查历史：exam_history_type, exam_history_detail, previous_exam_history (新增)")
            print("   - 生活方式：exercise_frequency, lifestyle (扩展)")
            
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            db.session.rollback()

if __name__ == '__main__':
    update_database()

