"""
修复空密码哈希的脚本
检查并修复数据库中 password_hash 为空或格式错误的用户
"""
import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(backend_dir)

sys.path.insert(0, backend_dir)
sys.path.insert(1, parent_dir)

from load_env import load_environment
load_environment()

from models import db, User
from werkzeug.security import generate_password_hash

def fix_empty_password_hash():
    """修复空密码哈希"""
    try:
        # 查找所有用户
        users = User.query.all()
        
        empty_hash_users = []
        for user in users:
            if not user.password_hash or not user.password_hash.strip():
                empty_hash_users.append(user)
        
        if not empty_hash_users:
            print("✅ 所有用户的密码哈希都正常")
            return
        
        print(f"⚠️  发现 {len(empty_hash_users)} 个用户的密码哈希为空:")
        for user in empty_hash_users:
            print(f"  - ID: {user.id}, 用户名: {user.username}, 真实姓名: {user.real_name}")
        
        # 询问是否重置密码
        print("\n是否要重置这些用户的密码？")
        print("(将设置为默认密码: 123456)")
        
        # 默认密码
        default_password = "123456"
        
        for user in empty_hash_users:
            try:
                user.password_hash = generate_password_hash(default_password)
                db.session.add(user)
                print(f"✅ 已重置用户 {user.username} 的密码为: {default_password}")
            except Exception as e:
                print(f"❌ 重置用户 {user.username} 的密码失败: {e}")
        
        db.session.commit()
        print("\n✅ 密码重置完成")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_empty_password_hash()

