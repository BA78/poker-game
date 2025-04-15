"""
라우트 정의
"""
from flask import render_template, request, redirect, url_for, session, g, current_app, has_request_context
from .models.game import Game
import logging
import traceback

def register_routes(app):
    """라우트 등록"""
    
    # 로거 설정
    logger = logging.getLogger(__name__)
    
    # 게임 인스턴스 가져오기 함수
    def get_game():
        if 'game' not in session:
            session['game'] = {}
        
        if not hasattr(g, 'game'):
            g.game = Game()
            g.game.load_from_session(session['game'])
            logger.debug("게임 인스턴스 생성 또는 세션에서 로드됨")
        return g.game
    
    # 게임 인스턴스 저장 함수
    def save_game(game):
        """세션에 게임 상태 저장"""
        try:
            session['game'] = game.save_to_session()
            session.modified = True  # 세션 변경 명시적 알림
        except RuntimeError as e:
            logger.warning("요청 컨텍스트 외부에서 game 저장 시도\n%s", traceback.format_exc())
        except Exception as e:
            logger.error(f"게임 저장 오류: {str(e)}")
    
    @app.route('/')
    def index():
        """메인 페이지"""
        return render_template('index.html')

    @app.route('/play/computer')
    def play_computer():
        """컴퓨터와 대전"""
        game = get_game()
        game.reset_game()  # 완전한 초기화
        game.current_turn = None  # 명시적으로 None으로 설정하여 새 게임 버튼 표시
        save_game(game)
        
        # 세션 확인 및 디버깅 로그
        logger.info("컴퓨터 게임 페이지 로드: 게임 상태 초기화됨")
        
        return render_template('computer.html')

    @app.route('/play/human')
    def play_human():
        """사람과 대전 (기능 구현 예정)"""
        game = get_game()
        game.reset_game()
        return render_template('human.html')

    @app.route('/start')
    def start_game():
        """게임 시작"""
        try:
            game = get_game()
            
            # 게임이 이미 진행 중인지 확인
            if game.current_turn is not None and game.current_turn > 1:
                # 이미 진행 중인 게임이면 현재 상태 반환
                logger.info("이미 진행 중인 게임입니다.")
                return render_template('computer.html', **game.get_game_state())
            
            # 완전히 새 게임 시작
            logger.info("새 게임 시작")
            game.reset_game()
            game.start_game()
            save_game(game)
            
            return render_template('computer.html', **game.get_game_state())
        except Exception as e:
            logger.error(f"게임 시작 오류: {str(e)}")
            return render_template('error.html', error=str(e))

    @app.route('/discard', methods=['POST'])
    def discard_cards():
        """카드 버리기"""
        game = get_game()
        
        try:
            discard_indices = request.form.get('discard', '')
            discard_indices = [int(i) for i in discard_indices.split(',') if i.isdigit()]
            
            # 최대 5장 제한 검증
            MAX_CARDS_TO_DISCARD = 5
            if len(discard_indices) > MAX_CARDS_TO_DISCARD:
                raise ValueError(f"최대 {MAX_CARDS_TO_DISCARD}장의 카드만 교체할 수 있습니다.")
            
            game.discard_cards('Player 1', discard_indices)
            save_game(game)
            
            if game.current_turn is None:  # 게임 종료
                return render_template('computer.html', **game.get_game_state())
            
            # start_game으로 리다이렉트하지 않고 현재 상태 렌더링
            return render_template('computer.html', **game.get_game_state())
        except Exception as e:
            app.logger.error(f"카드 버리기 오류: {str(e)}")
            return render_template('error.html', error=str(e))
    
    @app.route('/hand-rankings')
    def hand_rankings():
        """족보 확인 페이지"""
        return render_template('hand_rankings.html')

    @app.route('/next_turn')
    def next_turn():
        """턴 넘기기"""
        game = get_game()
        try:
            # 게임 상태 검증
            error = validate_game_state(game)
            if error:
                return render_template('error.html', error=error)
            
            game.next_turn()
            save_game(game)
            
            return render_template('computer.html', **game.get_game_state())
        except Exception as e:
            logger.error(f"턴 넘기기 오류: {str(e)}")
            return render_template('error.html', error=str(e))
            
    @app.teardown_appcontext
    def close_game(error):
        if not has_request_context():
            return

        if request.path.startswith('/static'):
            return  # 정적 자원에 대해선 저장 로직 건너뜀

        try:
            if hasattr(g, 'game'):
                session['game'] = g.game.save_to_session()
                session.modified = True
        except Exception as e:
            app.logger.warning("game 저장 중 오류: %s", e)

    @app.route('/new_game')
    def new_game():
        """명시적으로 새 게임 시작"""
        game = get_game()
        game.reset_game()
        save_game(game)
        logger.info("새 게임 준비")
        return redirect(url_for('play_computer'))

def validate_game_state(game):
    """게임 상태 검증"""
    if not game:
        return "게임이 초기화되지 않았습니다."
    
    if game.current_turn is None:
        return "게임이 이미 종료되었습니다."
    
    return None  # 게임 상태가 유효함 