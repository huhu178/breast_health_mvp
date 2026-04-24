"""
装饰器工具
"""
from functools import wraps
from flask import session, jsonify, g
import inspect


def login_required(f):
    """登录验证装饰器
    - 支持两种用法：
      1) 视图函数签名包含 current_user 参数 → 传入用户对象
      2) 视图函数不包含该参数 → 仅在 g 上下文设置 user_id/current_user
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'code': 401, 'message': '未登录或登录已过期'}), 401

        # 兼容导入，避免循环依赖
        current_user = None
        try:
            from models import User  # 延迟导入
            current_user = User.query.get(user_id)
        except Exception:
            current_user = None

        # 注入到全局上下文
        g.user_id = user_id
        g.current_user = current_user

        # 根据函数签名决定是否传入 current_user
        try:
            sig = inspect.signature(f)
            if 'current_user' in sig.parameters:
                return f(current_user, *args, **kwargs)
        except Exception:
            pass
        return f(*args, **kwargs)

    return decorated_function


def c_end_verify(f):
    """C端访问校验占位装饰器
    - 如需对C端访问进行手机验证码/令牌校验，可在此扩展
    - 当前实现为直通，保持与现有路由兼容
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper
