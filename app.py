from flask import Flask, render_template, request, redirect, url_for
from game import PokerGame
from typing import List

app = Flask(__name__)
app.config.from_pyfile('config.py')

game = PokerGame()

@app.route('/')
def index():
    return render_template('index.html', players=None, scores=None, current_turn=None)

@app.route('/play/computer')
def play_computer():
    game.current_turn = 1
    return render_template('index.html', players=None, scores=None, 
                         current_turn=game.current_turn)

@app.route('/start')
def start_game():
    game.start_game()
    return render_template('index.html', players=game.hands, scores=game.scores, 
                         current_turn=game.current_turn)

@app.route('/discard', methods=['POST'])
def discard_cards():
    discard_indices = request.form.get('discard', '')
    discard_indices = [int(i) for i in discard_indices.split(',') if i.isdigit()]
    
    game.discard_cards(discard_indices)
    
    if game.current_turn is None:  # 게임 종료
        return render_template('index.html', players=game.hands, scores=game.scores,
                            current_turn=None, winner=game.winner)
    
    return redirect(url_for('start_game'))

@app.route('/next_turn')
def next_turn():
    game.next_turn()
    
    if game.current_turn is None:  # 게임 종료
        return render_template('index.html', players=game.hands, scores=game.scores,
                            current_turn=None, winner=game.winner)
    
    return render_template('index.html', players=game.hands, scores=game.scores,
                         current_turn=game.current_turn)

if __name__ == '__main__':
    app.run(debug=True)