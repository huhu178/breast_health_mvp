"""
环境变量加载工具
自动从项目根目录的 .env 文件加载环境变量
"""
import os
import sys
from pathlib import Path

def load_environment():
    """加载环境变量"""
    # 获取项目根目录
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    env_file = project_root / '.env'
    
    if not env_file.exists():
        print("WARNING: .env file not found")
        print(f"    Please create .env file at: {env_file}")
        print(f"    Refer to env.example for template")
        return False
    
    try:
        # 尝试使用 python-dotenv
        try:
            from dotenv import load_dotenv
            # 强制使用 UTF-8 编码加载
            # 注意：默认 override=False，若进程环境已存在同名变量会导致 .env 修改不生效
            load_dotenv(env_file, encoding='utf-8', override=True)
            print(f"OK: Loaded environment variables from .env")
            return True
        except ImportError:
            # 如果没有安装 python-dotenv，手动解析
            print("INFO: python-dotenv not installed, using simple parser")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    # 解析 KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
            print(f"OK: Manually parsed .env file")
            return True
    except Exception as e:
        print(f"ERROR: Failed to load .env file: {e}")
        return False

def check_required_env_vars():
    """检查必需的环境变量"""
    required_vars = {
        'DATABASE_URL': '数据库连接字符串',
        'SECRET_KEY': 'Flask 密钥',
        'OPENROUTER_API_KEY': 'OpenRouter API Key'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        print("\nERROR: Missing required environment variables:")
        for var in missing_vars:
            print(var)
        print("\nPlease configure these variables in .env file")
        return False
    
    return True

if __name__ == '__main__':
    # 测试环境变量加载
    load_environment()
    check_required_env_vars()
    
    # 显示当前配置（隐藏敏感信息）
    print("\nCurrent Configuration:")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not configured')[:30]}...")
    print(f"  SECRET_KEY: {'Configured' if os.getenv('SECRET_KEY') else 'Not configured'}")
    print(f"  OPENROUTER_API_KEY: {'Configured (sk-or-v1-...)' if os.getenv('OPENROUTER_API_KEY') else 'Not configured'}")
    print(f"  OPENROUTER_MODEL: {os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-pro')}")

