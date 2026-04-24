
# 首先加载环境变量
import sys
import os

# 添加路径设置
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
backend_dir = current_dir

# 重要：backend目录必须在最前面，优先级最高
# 这样可以确保 from models import 时导入的是 backend/models.py
# 而不是根目录的旧 models.py
if backend_dir in sys.path:
    sys.path.remove(backend_dir)
if parent_dir in sys.path:
    sys.path.remove(parent_dir)

sys.path.insert(0, backend_dir)  # 第一优先级：backend目录
sys.path.insert(1, parent_dir)   # 第二优先级：父目录（用于导入config）

from load_env import load_environment
load_environment()

from flask import Flask, send_from_directory, session, jsonify
from flask_cors import CORS
from config import Config
from models import db
import os

def create_app():
    """应用工厂函数 - 支持 Vue 前端"""

    # === 检查必需的环境变量 ===
    from load_env import check_required_env_vars
    if not check_required_env_vars():
        # 只在生产环境强制退出
        if os.getenv('FLASK_ENV') == 'production':
            print("\n" + "="*60)
            print("❌ ERROR: Missing required environment variables!")
            print("Please check .env file configuration")
            print("="*60 + "\n")
            import sys
            sys.exit(1)
        else:
            print("⚠️  WARNING: Some environment variables are missing")
            print("   This is OK in development mode")
            print("   The app will use default values from config.py\n")

    # 检测 Vue 构建目录是否存在
    vue_build_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'frontend', 'vue-app', 'dist'
    )
    
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'frontend', 'templates'
    )
    static_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'frontend', 'static'
    )

    if os.path.exists(vue_build_dir):
        print(f"OK: Vue build directory detected: {vue_build_dir}")
        print("INFO: Using Vue build frontend")
        # 使用 Vue 构建目录作为静态文件目录
        app = Flask(
            __name__,
            static_folder=vue_build_dir,
            static_url_path='',
            template_folder=template_dir
        )
    else:
        print(f"WARNING: Vue build directory not found: {vue_build_dir}")
        print("INFO: Please run: cd frontend/vue-app && npm run build")
        print("INFO: Using traditional template mode")
        # 回退到传统模板模式
        app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # 根据环境加载不同的配置
    if os.getenv('FLASK_ENV') == 'production':
        # 生产环境：使用 config_prod.py 中的 ProductionConfig
        try:
            from config_prod import ProductionConfig
            app.config.from_object(ProductionConfig)
            print("✅ Loaded production config from config_prod.py")
        except ImportError:
            # 如果没有 config_prod.py，使用默认 Config
            app.config.from_object(Config)
            print("⚠️  config_prod.py not found, using default Config")
    else:
        # 开发环境：使用 config.py 中的 Config
        app.config.from_object(Config)
        print("✅ Loaded development config from config.py")
    
    # 初始化扩展
    db.init_app(app)
    
    # CORS 配置 - 根据环境自动配置
    if os.getenv('FLASK_ENV') == 'production':
        # 生产环境：从环境变量读取允许的源
        cors_origins = os.getenv('CORS_ORIGINS', '')
        if cors_origins:
            # 如果配置了 CORS_ORIGINS，使用配置的域名/IP
            allowed_origins = [origin.strip() for origin in cors_origins.split(',')]
            print(f"✅ CORS enabled for: {allowed_origins}")
        else:
            # 如果未配置（使用IP访问），允许所有来源
            allowed_origins = '*'
            print("⚠️  CORS_ORIGINS not set, allowing all origins (IP deployment)")
        CORS(app, supports_credentials=True, origins=allowed_origins)
    else:
        # 开发环境：允许 Vite 开发服务器
        CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'http://localhost:5000'])
        print("✅ CORS enabled for development (localhost:5173, localhost:5000)")
    
    # 注册蓝图
    from routes.auth_routes import auth_bp
    from routes.knowledge_routes import knowledge_bp
    
    # B端C端分离路由
    from routes.b_patient_management import b_patient_bp
    from routes.b_record_management import b_record_bp
    from routes.b_report_management import b_report_bp
    from routes.b_report_update import b_report_update_bp
    from routes.c_patient_service import c_patient_bp
    from routes.c_auth_routes import c_auth_bp
    from routes.miniprogram_routes import miniprogram_bp  # 微信小程序路由
    from routes.ai_tongue_platform_routes import ai_tongue_platform_bp  # AI舌诊开放平台（后端代调用）

    # 注册B端C端路由
    app.register_blueprint(b_patient_bp)
    app.register_blueprint(b_record_bp)
    app.register_blueprint(b_report_bp)
    app.register_blueprint(b_report_update_bp)  # 新增：报告审核相关API
    app.register_blueprint(c_patient_bp)
    app.register_blueprint(c_auth_bp)
    app.register_blueprint(miniprogram_bp)  # 微信小程序接口
    app.register_blueprint(ai_tongue_platform_bp)  # AI舌诊开放平台接口（小程序通过后端调用）
    
    # 注册基础路由
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(knowledge_bp)
    
    # ===== Vue SPA 路由处理 =====
    if os.path.exists(vue_build_dir):
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_vue_app(path):
            """
            服务 Vue 应用
            - 如果是 API 请求，让其通过到蓝图
            - 如果是静态资源，从 dist 目录提供
            - 其他所有请求都返回 index.html（支持 Vue Router history 模式）
            """
            # API 请求应该被路由系统处理，不应该到这里
            # 这里处理的是前端路由
            
            if path and os.path.exists(os.path.join(vue_build_dir, path)):
                # 如果文件存在（静态资源），直接返回
                return send_from_directory(vue_build_dir, path)
            else:
                # 否则返回 index.html，让 Vue Router 处理路由
                return send_from_directory(vue_build_dir, 'index.html')
        
        # 处理 404，支持 Vue Router 的 history 模式
        @app.errorhandler(404)
        def not_found(e):
            # 如果是 API 请求，返回 JSON 错误
            if '/api/' in str(e):
                return jsonify({
                    'success': False,
                    'message': '接口不存在'
                }), 404
            # 否则返回 Vue 应用的 index.html
            return send_from_directory(vue_build_dir, 'index.html')
    else:
        # 如果没有 Vue 构建，使用传统路由
        from flask import render_template, redirect, url_for
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/login')
        def login_page():
            return render_template('login.html')
        
        @app.route('/dashboard')
        def dashboard():
            if 'user_id' not in session:
                return redirect(url_for('login_page'))
            return render_template('dashboard.html', active_page='dashboard')
    
    # 健康检查接口
    @app.route('/api/health')
    def health_check():
        """健康检查"""
        # 脱敏数据库连接信息（只返回 host/port/db，不返回用户名/密码）
        import re
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '') or ''
        m = re.match(r'^[^:]+://[^:]+:[^@]+@([^:/]+)(?::(\d+))?/([^?]+)', db_url)
        db_info = None
        if m:
            db_info = {
                'host': m.group(1),
                'port': m.group(2),
                'db': m.group(3)
            }
        # 脱敏 LLM 配置状态（不返回 key）
        llm_enabled = bool(os.getenv('OPENROUTER_API_KEY', '').strip())
        llm_info = {
            'enabled': llm_enabled,
            'model': os.getenv('OPENROUTER_MODEL', 'google/gemini-2.5-pro')
        }
        return jsonify({
            'success': True,
            'message': 'OK',
            'frontend': 'Vue' if os.path.exists(vue_build_dir) else 'Jinja2',
            'database': db_info,
            'llm': llm_info
        })
    
    # C端测试页面
    @app.route('/test_c_api.html')
    def test_c_api():
        """C端API测试页面"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        return send_from_directory(frontend_dir, 'test_c_api.html')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 轻量自修复：db.create_all() 不会给已存在表自动加列，这里补齐小程序需要的字段
        try:
            from sqlalchemy import text
            from sqlalchemy import inspect

            inspector = inspect(db.engine)
            # users：补齐健康管理师微信号字段（用于小程序展示联系方式）
            if 'users' in inspector.get_table_names():
                cols = {c.get('name') for c in inspector.get_columns('users')}
                if 'wechat_id' not in cols:
                    db.session.execute(text("ALTER TABLE users ADD COLUMN wechat_id VARCHAR(50)"))
                    db.session.commit()
                    print("OK: Added missing column users.wechat_id")
            if 'b_reports' in inspector.get_table_names():
                cols = {c.get('name') for c in inspector.get_columns('b_reports')}
                if 'source_channel' not in cols:
                    # 默认来源：b_end；小程序生成的会写 miniprogram
                    db.session.execute(text("ALTER TABLE b_reports ADD COLUMN source_channel VARCHAR(50) DEFAULT 'b_end'"))
                    db.session.commit()
                    print("OK: Added missing column b_reports.source_channel")

            # C端：确保核心表存在（create_all会建表，但不会补列；C端目前未新增列，这里仅做存在性提示）
            for t in ('c_patients', 'c_health_records', 'c_reports'):
                if t not in inspector.get_table_names():
                    print(f"WARNING: Expected C-end table missing: {t}")

            # C端：补齐 c_health_records 舌诊字段（auto-migration）
            if 'c_health_records' in inspector.get_table_names():
                cols = {c.get('name') for c in inspector.get_columns('c_health_records')}
                if 'tongue_check_result_id' not in cols:
                    db.session.execute(text("ALTER TABLE c_health_records ADD COLUMN tongue_check_result_id VARCHAR(50)"))
                    db.session.commit()
                    print("OK: Added missing column c_health_records.tongue_check_result_id")
                if 'tongue_result_raw' not in cols:
                    db.session.execute(text("ALTER TABLE c_health_records ADD COLUMN tongue_result_raw TEXT"))
                    db.session.commit()
                    print("OK: Added missing column c_health_records.tongue_result_raw")
                if 'tongue_result_summary' not in cols:
                    db.session.execute(text("ALTER TABLE c_health_records ADD COLUMN tongue_result_summary TEXT"))
                    db.session.commit()
                    print("OK: Added missing column c_health_records.tongue_result_summary")
                if 'tongue_checked_at' not in cols:
                    db.session.execute(text("ALTER TABLE c_health_records ADD COLUMN tongue_checked_at TIMESTAMP"))
                    db.session.commit()
                    print("OK: Added missing column c_health_records.tongue_checked_at")
        except Exception as e:
            # 不阻塞启动，避免在无权限/只读数据库时报错
            print(f"WARNING: Auto-migration for b_reports.source_channel skipped: {e}")
        print("OK: Database tables created successfully!")
    
    return app

app = create_app()

if __name__ == '__main__':
    import subprocess
    import sys

    # 如果设置了环境变量 DISABLE_INTERNAL_VUE=1，则完全禁用 Flask 内部启动 Vite 的逻辑
    disable_internal_vue = os.getenv('DISABLE_INTERNAL_VUE') == '1'

    if not disable_internal_vue:
        # 只在主进程（非 reloader）中启动 Vue
        # 检查是否是 reloader 进程
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            vue_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'vue-app')
            if os.path.exists(vue_dir):
                print("INFO: Starting Vue development server...")
                try:
                    if sys.platform == 'win32':
                        # Windows: 使用 start 命令在新窗口启动
                        subprocess.Popen(
                            'start cmd /k "cd /d {} && npm run dev"'.format(vue_dir),
                            shell=True
                        )
                    else:
                        # Linux/Mac
                        subprocess.Popen(
                            ['npm', 'run', 'dev'],
                            cwd=vue_dir,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    print("OK: Vue development server start command executed")
                except Exception as e:
                    print(f"WARNING: Vue startup failed: {e}")
                    print("INFO: Please run manually: cd frontend/vue-app && npm run dev")
            else:
                print("WARNING: Vue directory not found, skip starting dev server")
    else:
        print("INFO: DISABLE_INTERNAL_VUE=1, skip internal Vue dev server startup")

    app = create_app()
    print("\n" + "="*60)
    print("Breast Health Management System Starting...")
    print("="*60)
    print("Flask API: http://localhost:5000")
    print("Vue Frontend: http://localhost:5173")
    print("API Health Check: http://localhost:5000/api/health")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)

 