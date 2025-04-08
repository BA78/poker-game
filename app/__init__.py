"""
Flask 앱 초기화
"""
from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect, CSRFError

def create_app(config_name=None):
    """Flask 앱 생성"""
    # 앱 기본 설정
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # 프로젝트 루트 디렉토리를 Python 경로에 추가
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 환경 설정 로드
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('config.production')
    else:
        app.config.from_object('config.settings')

    # Jinja2 환경에 zip 함수 추가
    app.jinja_env.globals.update(zip=zip)

    # 세션 설정
    app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # CSRF 보호 설정
    csrf = CSRFProtect(app)
    
    # CSRF 에러 핸들러
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('error.html', error="보안 토큰이 만료되었습니다. 다시 시도해주세요."), 400
    
    # 로깅 설정
    setup_logging(app)
    
    # 라우트 등록
    from .routes import register_routes
    register_routes(app)

    return app

def setup_logging(app):
    """로깅 설정"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    file_handler = RotatingFileHandler('logs/poker.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    if app.config['DEBUG']:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)
        
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO if not app.config['DEBUG'] else logging.DEBUG)
    app.logger.info('포커 게임 시작') 