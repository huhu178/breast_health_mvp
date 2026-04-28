"""
修复结节数量字段类型：将 Integer 改为 String 以支持 'single'/'multiple' 等值
执行方式：python backend/scripts/fix_nodule_count_fields.py
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

def fix_nodule_count_fields():
    with app.app_context():
        try:
            print("开始修复结节数量字段类型...")
            
            # 检查 thyroid_nodule_count 字段类型
            check_sql = """
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'b_health_records' 
                AND column_name = 'thyroid_nodule_count'
            """
            result = db.session.execute(db.text(check_sql)).fetchone()
            
            if result:
                current_type = result[0]
                print(f"当前 thyroid_nodule_count 类型: {current_type}")
                
                if current_type == 'character varying' or current_type == 'varchar':
                    print("[跳过] thyroid_nodule_count 已经是 String 类型")
                elif current_type == 'integer':
                    print("[执行] 开始迁移 thyroid_nodule_count...")
                    
                    # 1. 添加新的 String 类型列
                    print("步骤 1: 添加新的 String 类型列...")
                    try:
                        db.session.execute(db.text("""
                            ALTER TABLE b_health_records 
                            ADD COLUMN IF NOT EXISTS thyroid_nodule_count_new VARCHAR(20)
                        """))
                        print("[成功] 新列添加完成")
                    except Exception as e:
                        if 'already exists' in str(e):
                            print("[跳过] 新列已存在")
                        else:
                            raise
                    
                    # 2. 将现有 Integer 值转换为 String（如果有数据）
                    print("步骤 2: 转换现有数据...")
                    try:
                        result = db.session.execute(db.text("""
                            UPDATE b_health_records 
                            SET thyroid_nodule_count_new = CAST(thyroid_nodule_count AS VARCHAR) 
                            WHERE thyroid_nodule_count IS NOT NULL
                        """))
                        print(f"[成功] 转换了 {result.rowcount} 条记录")
                    except Exception as e:
                        if 'column "thyroid_nodule_count" does not exist' in str(e):
                            print("[跳过] 原列不存在")
                        else:
                            raise
                    
                    # 3. 删除旧列
                    print("步骤 3: 删除旧 Integer 列...")
                    try:
                        db.session.execute(db.text("""
                            ALTER TABLE b_health_records 
                            DROP COLUMN IF EXISTS thyroid_nodule_count
                        """))
                        print("[成功] 旧列删除完成")
                    except Exception as e:
                        print(f"[警告] 删除旧列时出错: {str(e)[:100]}")
                    
                    # 4. 重命名新列为原列名
                    print("步骤 4: 重命名新列...")
                    try:
                        db.session.execute(db.text("""
                            ALTER TABLE b_health_records 
                            RENAME COLUMN thyroid_nodule_count_new TO thyroid_nodule_count
                        """))
                        print("[成功] 列重命名完成")
                    except Exception as e:
                        if 'does not exist' in str(e):
                            print("[跳过] 新列不存在，可能已重命名")
                        else:
                            raise
                    
                    db.session.commit()
                    print("[成功] thyroid_nodule_count 字段类型修复完成！")
                else:
                    print(f"[警告] 未知类型: {current_type}")
            else:
                print("[警告] 未找到 thyroid_nodule_count 列")
            
            print("\n" + "="*50)
            print("[完成] 所有字段检查完成！")
            print("="*50 + "\n")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[错误] 修复失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_nodule_count_fields()

