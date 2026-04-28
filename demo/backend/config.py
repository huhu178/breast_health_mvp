
"""
配置文件
"""
import os

# 强制设置 PostgreSQL 客户端编码为 UTF-8
os.environ['PGCLIENTENCODING'] = 'UTF8'

class Config:
    """应用配置"""

    # 数据库配置（生产环境必须从环境变量读取）
    _database_url = os.getenv('DATABASE_URL')
    if not _database_url:
        if os.getenv('FLASK_ENV') == 'production':
            raise ValueError("❌ DATABASE_URL environment variable is required in production")
        else:
            # 开发环境：必须在 .env 文件中配置 DATABASE_URL
            print("=" * 60)
            print("⚠️  WARNING: DATABASE_URL not configured!")
            print("=" * 60)
            print("Please add DATABASE_URL to your .env file:")
            print("")
            print("For PostgreSQL:")
            print("  DATABASE_URL=postgresql://postgres:Maqing123%40@localhost:5433/jiejie")
            print("")
            print("Example .env file:")
            print("  cp .env (from your current .env)")
            print("=" * 60)
            raise ValueError("DATABASE_URL is required. Please configure .env file.")
    
    SQLALCHEMY_DATABASE_URI = _database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLAlchemy Engine 配置：强制使用 UTF-8 编码
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'client_encoding': 'utf8',
            'options': '-c client_encoding=utf8'
        },
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'echo': False
    }
    
    # 密钥配置（生产环境必须从环境变量读取）
    _secret_key = os.getenv('SECRET_KEY')
    _jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    
    # 生产环境强制要求密钥
    if os.getenv('FLASK_ENV') == 'production':
        if not _secret_key:
            raise ValueError("SECRET_KEY environment variable is required in production")
        if not _jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY environment variable is required in production")
        SECRET_KEY = _secret_key
        JWT_SECRET_KEY = _jwt_secret_key
    else:
        # 开发环境使用默认值
        SECRET_KEY = _secret_key or 'dev-secret-key-change-in-production'
        JWT_SECRET_KEY = _jwt_secret_key or 'dev-jwt-secret-key-change-in-production'
    
    # JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 60 * 60  # 7天
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    # LLM配置（OpenRouter）
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')  # 从环境变量读取
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-pro')  # 默认使用gemini 2.5 pro

    # ========================================
    # 第三方插件配置：AI舌诊（小程序插件）
    # ========================================
    # @isdoc 小程序插件 idCode（外部平台审核通过后提供），用于 plugin.init
    AI_TONGUE_ID_CODE = os.getenv('AI_TONGUE_ID_CODE', '')

