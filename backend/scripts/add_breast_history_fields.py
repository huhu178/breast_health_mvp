"""
执行数据库迁移：添加乳腺基础疾病史和其他风险因素字段
执行方式：python backend/scripts/add_breast_history_fields.py
"""
import sys
import os
import io

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app()

def add_columns():
    """添加缺失的字段到数据库表"""
    with app.app_context():
        try:
            # 定义需要添加的字段列表
            columns = [
                # 乳腺基础疾病史字段
                ('breast_hyperplasia_history', 'VARCHAR(50)', '乳腺增生病史'),
                ('breast_fibroadenoma_history', 'VARCHAR(50)', '乳腺纤维瘤病史'),
                ('breast_cyst_history', 'VARCHAR(50)', '乳腺囊肿病史'),
                ('breast_inflammation_history', 'VARCHAR(50)', '乳腺炎病史'),
                ('breast_cancer_history', 'VARCHAR(50)', '乳腺癌病史'),
                # 其他风险因素字段
                ('dust_exposure_history', 'VARCHAR(50)', '粉尘/有害气体接触史'),
                ('diabetes_history', 'VARCHAR(50)', '糖尿病'),
                ('radiation_exposure_history', 'VARCHAR(200)', '辐射暴露史'),
                ('radiation_other', 'VARCHAR(200)', '其他辐射暴露'),
                ('autoimmune_disease_history', 'VARCHAR(200)', '自身免疫疾病'),
                ('autoimmune_other', 'VARCHAR(200)', '其他自身免疫疾病'),
                ('medication_history', 'VARCHAR(200)', '药物使用史'),
                ('medication_other', 'VARCHAR(200)', '其他药物使用'),
                ('tumor_marker_test', 'VARCHAR(50)', '肿瘤标志物检查'),
                ('hereditary_breast_history', 'VARCHAR(50)', '遗传性乳腺病史'),
                # 乳腺结节数量字段
                ('nodule_count', 'VARCHAR(20)', '乳腺结节数量'),
            ]
            
            print("开始执行数据库迁移...")
            print(f"需要添加 {len(columns)} 个字段\n")
            
            success_count = 0
            skip_count = 0
            error_count = 0
            
            for column_name, column_type, description in columns:
                try:
                    # 检查字段是否已存在
                    check_sql = f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'b_health_records' 
                        AND column_name = '{column_name}'
                    """
                    result = db.session.execute(db.text(check_sql)).fetchone()
                    
                    if result:
                        print(f"[跳过] {column_name} ({description}) - 字段已存在")
                        skip_count += 1
                    else:
                        # 添加字段
                        alter_sql = f"ALTER TABLE b_health_records ADD COLUMN {column_name} {column_type}"
                        db.session.execute(db.text(alter_sql))
                        print(f"[成功] {column_name} ({description}) - 添加成功")
                        success_count += 1
                        
                except Exception as e:
                    error_msg = str(e)
                    # 如果字段已存在，跳过
                    if 'already exists' in error_msg or 'duplicate column' in error_msg.lower():
                        print(f"[跳过] {column_name} ({description}) - 字段已存在")
                        skip_count += 1
                    else:
                        print(f"[失败] {column_name} ({description}) - 添加失败: {error_msg[:100]}")
                        error_count += 1
            
            db.session.commit()
            
            print(f"\n{'='*50}")
            print(f"迁移完成！")
            print(f"[成功] 成功添加: {success_count} 个字段")
            print(f"[跳过] 已存在跳过: {skip_count} 个字段")
            print(f"[失败] 失败: {error_count} 个字段")
            print(f"{'='*50}\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"[错误] 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_columns()

