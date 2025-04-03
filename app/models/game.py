"""
게임 관련 클래스 정의
"""
import random
from typing import Dict, List, Optional
from app.models.card import Card
from app.models.player import Player
from app.models.ai import PokerAI
from config.settings import SUITS, RANKS, CARDS_PER_HAND, MAX_TURNS

class Game:
    """포커 게임 클래스"""
    def __init__(self):
        self.reset_game()

    def reset_game(self) -> None:
        """게임 초기화"""
        self.players = {}
        self.current_turn = None
        self.max_turns = MAX_TURNS
        self.winner = None

    def start_game(self) -> None:
        """게임 시작"""
        if self.current_turn is not None and self.current_turn > 1:
            return

        # 플레이어 초기화
        self.players = {
            'Player 1': Player('Player 1'),
            'Computer': Player('Computer')
        }

        # 덱 생성 및 섞기
        full_deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(full_deck)

        # 각 플레이어에게 덱 분배
        deck_size = len(full_deck) // 2
        self.players['Player 1'].deck = full_deck[:deck_size]
        self.players['Computer'].deck = full_deck[deck_size:]

        # 초기 카드 분배
        for player in self.players.values():
            player.draw_initial_cards(CARDS_PER_HAND)

        self.current_turn = 1

    def discard_cards(self, player_name: str, indices: List[int]) -> None:
        """카드 버리기"""
        if not indices:
            self.next_turn()
            return

        player = self.players[player_name]
        player.discard_cards(indices)
        self.next_turn()

    def next_turn(self) -> None:
        """다음 턴으로 진행"""
        if self.current_turn < self.max_turns:
            self.current_turn += 1
            self._handle_computer_turn()
        else:
            self.determine_winner()

    def _handle_computer_turn(self) -> None:
        """컴퓨터의 턴 처리"""
        computer = self.players['Computer']
        ai = PokerAI(computer.hand)
        indices_to_discard = ai.decide_cards_to_discard()

        if indices_to_discard:
            computer.discard_cards(indices_to_discard)

    def determine_winner(self) -> None:
        """승자 결정"""
        player_score = self.players['Player 1'].score[0]
        computer_score = self.players['Computer'].score[0]
        
        if player_score > computer_score:
            self.winner = 'Player 1'
        elif player_score < computer_score:
            self.winner = 'Computer'
        else:
            self.winner = 'Draw'
        self.current_turn = None

    def get_game_state(self) -> Dict:
        """현재 게임 상태 반환"""
        return {
            'hands': {name: player.get_hand_dict() 
                     for name, player in self.players.items()},
            'scores': {name: player.score 
                      for name, player in self.players.items()},
            'previous_scores': {name: player.previous_score 
                              for name, player in self.players.items()
                              if player.previous_score is not None},
            'card_changes': {name: player.card_changes
                           for name, player in self.players.items()
                           if player.card_changes['discarded'] or player.card_changes['drawn']},
            'current_turn': self.current_turn,
            'max_turns': self.max_turns,
            'winner': self.winner
        } 