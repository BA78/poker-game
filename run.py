"""
앱 실행
"""
import os
from app import create_app

# 환경 변수에서 설정 가져오기
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    debug = False # env != 'production'
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=debug, use_reloader=False) 