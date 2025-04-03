from flask import Flask, render_template, request, redirect, url_for
from game import PokerGame
from typing import List

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Jinja2 환경에 zip 함수 추가
app.jinja_env.globals.update(zip=zip)

game = PokerGame()

@app.route('/')
def index():
    return render_template('index.html', 
                         players=game.hands if game.hands else None,
                         scores=game.scores if game.scores else None,
                         previous_scores=game.previous_scores if hasattr(game, 'previous_scores') else None,
                         current_turn=game.current_turn,
                         max_turns=game.max_turns,
                         winner=game.winner,
                         card_changes=game.card_changes if hasattr(game, 'card_changes') else None)

@app.route('/play/computer')
def play_computer():
    game.current_turn = 1
    return render_template('index.html', 
                         players=None, 
                         scores=None,
                         previous_scores=None,
                         current_turn=game.current_turn, 
                         max_turns=game.max_turns)

@app.route('/start')
def start_game():
    game.start_game()
    return render_template('index.html', 
                         players=game.hands, 
                         scores=game.scores,
                         previous_scores=game.previous_scores,
                         current_turn=game.current_turn, 
                         max_turns=game.max_turns)

@app.route('/discard', methods=['POST'])
def discard_cards():
    discard_indices = request.form.get('discard', '')
    discard_indices = [int(i) for i in discard_indices.split(',') if i.isdigit()]
    
    game.discard_cards(discard_indices)
    
    if game.current_turn is None:  # 게임 종료
        return render_template('index.html', 
                            players=game.hands, 
                            scores=game.scores,
                            previous_scores=game.previous_scores,
                            current_turn=None, 
                            winner=game.winner, 
                            max_turns=game.max_turns)
    
    return redirect(url_for('start_game'))

@app.route('/next_turn')
def next_turn():
    game.next_turn()
    
    if game.current_turn is None:  # 게임 종료
        return render_template('index.html', 
                            players=game.hands, 
                            scores=game.scores,
                            previous_scores=game.previous_scores,
                            current_turn=None, 
                            winner=game.winner, 
                            max_turns=game.max_turns)
    
    return render_template('index.html', 
                         players=game.hands, 
                         scores=game.scores,
                         previous_scores=game.previous_scores,
                         current_turn=game.current_turn, 
                         max_turns=game.max_turns)

if __name__ == '__main__':
    app.run(debug=True)