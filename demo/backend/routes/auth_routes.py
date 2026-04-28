"""
B端用户认证路由
处理健康管理师的登录、注册、登出
"""
from flask import Blueprint, request, session, jsonify
from models import db, User
from utils.response import Response
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    注册新用户（健康管理师）
    
    请求体:
    {
        "username": "admin",
        "password": "123456",
        "real_name": "管理员",
        "email": "admin@example.com",  // 可选
        "phone": "13800138000"  // 可选
    }
    
    响应:
    {
        "success": true,
        "message": "注册成功",
        "data": {
            "user": { ... }
        }
    }
    """
    data = request.json or {}
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    real_name = data.get('real_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    
    # 验证必填字段
    if not username:
        return Response.error('用户名不能为空', 400)
    if not password:
        return Response.error('密码不能为空', 400)
    if len(password) < 6:
        return Response.error('密码长度至少6位', 400)
    
    try:
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return Response.error('用户名已存在', 400)
        
        # 创建新用户
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            real_name=real_name or username,
            email=email or None,
            phone=phone or None,
            role='health_manager',
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return Response.success({
            'user': new_user.to_dict()
        }, '注册成功')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 注册失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error(f'注册失败: {str(e)}', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求体:
    {
        "username": "admin",
        "password": "123456"
    }
    
    响应:
    {
        "success": true,
        "message": "登录成功",
        "data": {
            "user": { ... }
        }
    }
    """
    data = request.json or {}
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return Response.error('用户名和密码不能为空', 400)
    
    try:
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return Response.error('用户名或密码错误', 401)
        
        if not user.is_active:
            return Response.error('账号已被禁用', 403)
        
        # 检查密码哈希是否存在
        if not user.password_hash or not user.password_hash.strip():
            # 开发阶段：如果密码哈希为空，自动将当前输入的密码设置为新密码
            # 这样可以避免管理员手工修库
            user.password_hash = generate_password_hash(password)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            return Response.success({
                'user': user.to_dict()
            }, '首次登录已为您初始化密码')
        
        # 验证密码
        try:
            if not check_password_hash(user.password_hash, password):
                return Response.error('用户名或密码错误', 401)
        except ValueError as e:
            # 密码哈希格式错误：自动修复为当前输入密码的哈希，并允许登录
            print(f"❌ 密码哈希格式错误，自动修复: {e}")
            user.password_hash = generate_password_hash(password)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True
            
            return Response.success({
                'user': user.to_dict()
            }, '密码已自动修复并登录成功')
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 设置会话
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True  # 设置会话为永久（根据配置的过期时间）

        # 保存机构类型（医院/社区/药店/健康体检中心）
        org_type = data.get('org_type', '').strip()
        if org_type:
            session['org_type'] = org_type

        user_dict = user.to_dict()
        user_dict['org_type'] = session.get('org_type', '')

        return Response.success({
            'user': user_dict
        }, '登录成功')
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 登录失败: {e}")
        import traceback
        traceback.print_exc()
        return Response.error(f'登录失败: {str(e)}', 500)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    用户登出
    
    响应:
    {
        "success": true,
        "message": "登出成功"
    }
    """
    try:
        session.clear()
        return Response.success(None, '登出成功')
    except Exception as e:
        print(f"❌ 登出失败: {e}")
        return Response.error(f'登出失败: {str(e)}', 500)


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    获取当前登录用户信息
    
    响应:
    {
        "success": true,
        "data": {
            "user": { ... }
        }
    }
    """
    user_id = session.get('user_id')
    
    if not user_id:
        return Response.error('未登录', 401)
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            session.clear()
            return Response.error('用户不存在', 401)
        
        if not user.is_active:
            session.clear()
            return Response.error('账号已被禁用', 403)
        
        return Response.success({
            'user': {**user.to_dict(), 'org_type': session.get('org_type', '')}
        })
        
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")
        return Response.error(f'获取用户信息失败: {str(e)}', 500)

