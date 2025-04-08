"""
프로덕션 환경 설정
"""
from config.settings import *

# 디버그 모드 비활성화
DEBUG = False

# 추가 보안 설정
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
REMEMBER_COOKIE_SECURE = True
REMEMBER_COOKIE_HTTPONLY = True
