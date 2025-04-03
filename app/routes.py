"""
라우트 정의
"""
from flask import render_template, request, redirect, url_for
from .models.game import Game

game = Game()

def register_routes(app):
    """라우트 등록"""
    @app.route('/')
    def index():
        """메인 페이지"""
        state = game.get_game_state()
        return render_template('index.html', **state)

    @app.route('/play/computer')
    def play_computer():
        """컴퓨터와 대전"""
        game.reset_game()
        return render_template('index.html')

    @app.route('/start')
    def start_game():
        """게임 시작"""
        game.start_game()
        return render_template('index.html', **game.get_game_state())

    @app.route('/discard', methods=['POST'])
    def discard_cards():
        """카드 버리기"""
        discard_indices = request.form.get('discard', '')
        discard_indices = [int(i) for i in discard_indices.split(',') if i.isdigit()]
        
        game.discard_cards('Player 1', discard_indices)
        state = game.get_game_state()
        
        if game.current_turn is None:  # 게임 종료
            return render_template('index.html', **state)
        
        return redirect(url_for('start_game'))

    @app.route('/next_turn')
    def next_turn():
        """턴 넘기기"""
        game.next_turn()
        state = game.get_game_state()
        
        if game.current_turn is None:  # 게임 종료
            return render_template('index.html', **state)
        
        return render_template('index.html', **state) 