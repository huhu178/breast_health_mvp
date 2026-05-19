"""
环境变量加载工具
自动从项目根目录的 .env 文件加载环境变量
"""
import os
import sys
import re
from pathlib import Path

ENV_LINE_RE = re.compile(r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$')


def _parse_env_value(raw_value):
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _load_env_file(env_file):
    loaded = 0
    skipped = 0
    with open(env_file, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            match = ENV_LINE_RE.match(line)
            if not match:
                skipped += 1
                continue
            key, raw_value = match.groups()
            os.environ.setdefault(key, _parse_env_value(raw_value))
            loaded += 1
    return loaded, skipped

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
        loaded, skipped = _load_env_file(env_file)
        if skipped:
            print(f"OK: Loaded environment variables from .env ({loaded} loaded, {skipped} invalid lines skipped)")
        else:
            print("OK: Loaded environment variables from .env")
        return True
    except Exception as e:
        print(f"ERROR: Failed to load .env file: {e}")
        return False

def check_required_env_vars():
    """检查必需的环境变量"""
    required_vars = {
        'DATABASE_URL': '数据库连接字符串',
        'SECRET_KEY': 'Flask 密钥',
        'OPENROUTER_API_KEY': 'OpenRouter API Key（使用DashScope时可不配）'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if 'OPENROUTER_API_KEY' in [item.split(':', 1)[0].strip('  -') for item in missing_vars] and os.getenv('DASHSCOPE_API_KEY'):
        missing_vars = [item for item in missing_vars if not item.strip().startswith('- OPENROUTER_API_KEY:')]

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
    print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'openrouter')}")
    print(f"  OPENROUTER_API_KEY: {'Configured (sk-or-v1-...)' if os.getenv('OPENROUTER_API_KEY') else 'Not configured'}")
    print(f"  DASHSCOPE_API_KEY: {'Configured (sk-...)' if os.getenv('DASHSCOPE_API_KEY') else 'Not configured'}")
    print(f"  OPENROUTER_MODEL: {os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-pro')}")
    print(f"  DASHSCOPE_MODEL: {os.getenv('DASHSCOPE_MODEL', 'qwen-plus')}")
