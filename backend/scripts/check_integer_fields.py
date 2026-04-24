"""
检查 b_health_records 表中的 Integer 类型字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app()

with app.app_context():
    result = db.session.execute(db.text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'b_health_records' 
        AND data_type = 'integer'
        ORDER BY column_name
    """))
    
    print("b_health_records 表中的 Integer 类型字段：")
    print("=" * 50)
    for row in result:
        print(f"{row[0]}: {row[1]}")

