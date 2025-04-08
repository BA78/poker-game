# poker-game
Flask 기반 멀티플레이 포커 게임

Flask 기반의 웹 포커 게임 애플리케이션입니다.

## 기능

- 컴퓨터와의 5턴 포커 게임
- 카드 교체 및 족보 판정
- 지능형 컴퓨터 AI

## 설치 및 실행

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 실행
python run.py
```

## 개발 정보

- Flask 3.0.2
- Python 3.8+
- CSS/JavaScript

## 프로젝트 구조

- `app/`: 애플리케이션 코드
  - `models/`: 게임 모델 (카드, 플레이어, AI 등)
  - `static/`: CSS, JavaScript 파일
  - `templates/`: HTML 템플릿
- `config/`: 설정 파일
- `tests/`: 테스트 코드
