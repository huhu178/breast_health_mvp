"""
生产环境配置
严格模式：所有敏感配置必须从环境变量读取
"""
import os


class ProductionConfig:
    """生产环境配置"""

    # ========================================
    # 数据库配置（必填）
    # ========================================
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("❌ DATABASE_URL environment variable is required in production")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 生产环境关闭SQL日志
    SQLALCHEMY_POOL_SIZE = 10  # 连接池大小
    SQLALCHEMY_POOL_RECYCLE = 3600  # 连接回收时间（秒）

    # ========================================
    # 密钥配置（必填）
    # ========================================
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'your-secret-key-change-in-production':
        raise ValueError("❌ SECRET_KEY must be set to a strong random value in production")

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY or JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
        raise ValueError("❌ JWT_SECRET_KEY must be set to a strong random value in production")

    # JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7天

    # ========================================
    # LLM配置（必填）
    # ========================================
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    if not OPENROUTER_API_KEY:
        raise ValueError("❌ OPENROUTER_API_KEY environment variable is required in production")

    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-pro')

    # ========================================
    # 应用配置
    # ========================================
    DEBUG = False
    TESTING = False
    ENV = 'production'

    # 分页配置
    ITEMS_PER_PAGE = 20

    # ========================================
    # 文件上传配置
    # ========================================
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/var/www/breast_health/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

    # ========================================
    # 安全配置
    # ========================================
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true').lower() in ('1', 'true', 'yes')  # @isdoc 仅HTTPS传输Cookie，可通过环境变量关闭
    SESSION_COOKIE_HTTPONLY = True  # @isdoc 防止XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # @isdoc CSRF防护

    # CORS配置（生产环境严格限制）
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    if not CORS_ORIGINS or CORS_ORIGINS == ['']:
        raise ValueError("❌ CORS_ORIGINS must be configured in production")

    # ========================================
    # 日志配置
    # ========================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/breast_health/app.log')

    # ========================================
    # 性能配置
    # ========================================
    # 启用JSON压缩
    JSONIFY_PRETTYPRINT_REGULAR = False

    # Redis配置（如果使用缓存）
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')


def validate_production_config():
    """验证生产环境配置"""
    errors = []

    # 检查数据库URL格式
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url.startswith('postgresql://'):
        errors.append("DATABASE_URL must use PostgreSQL")

    # 检查密钥强度
    secret = os.getenv('SECRET_KEY', '')
    if len(secret) < 32:
        errors.append("SECRET_KEY must be at least 32 characters long")

    jwt_secret = os.getenv('JWT_SECRET_KEY', '')
    if len(jwt_secret) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters long")

    # 检查API密钥
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    if not api_key.startswith('sk-or-'):
        errors.append("OPENROUTER_API_KEY format invalid")

    # 检查CORS配置
    cors = os.getenv('CORS_ORIGINS', '')
    if not cors or 'localhost' in cors:
        errors.append("CORS_ORIGINS should not include localhost in production")

    if errors:
        print("\n" + "="*60)
        print("❌ Production configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("="*60 + "\n")
        return False

    print("✅ Production configuration validated successfully")
    return True


# 在导入时验证配置
if os.getenv('FLASK_ENV') == 'production':
    validate_production_config()
