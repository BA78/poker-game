"""
Flask 앱 초기화
"""
from flask import Flask
import os

def create_app():
    """Flask 앱 생성"""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # 프로젝트 루트 디렉토리를 Python 경로에 추가
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app.config.from_object('config.settings')

    # Jinja2 환경에 zip 함수 추가
    app.jinja_env.globals.update(zip=zip)

    # 세션 설정
    app.secret_key = os.urandom(24)
    app.config['SESSION_TYPE'] = 'filesystem'

    # 라우트 등록
    from .routes import register_routes
    register_routes(app)

    return app 