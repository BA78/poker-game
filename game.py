from typing import Dict, List, Tuple
import random
from constants import *

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def to_dict(self) -> dict:
        return {'suit': self.suit, 'rank': self.rank}

class PokerGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self) -> None:
        self.players = {}
        self.hands = {}
        self.scores = {}
        self.current_turn = None
        self.max_turns = MAX_TURNS
        self.winner = None

    def create_deck(self) -> List[Card]:
        return [Card(suit, rank) for suit in SUITS for rank in RANKS]

    def start_game(self) -> None:
        if self.current_turn is not None and self.current_turn > 1:
            return

        full_deck = self.create_deck()
        
        # 플레이어와 컴퓨터의 덱 초기화
        self.players = {
            'Player 1': random.sample([card.to_dict() for card in full_deck], len(full_deck)),
            'Computer': random.sample([card.to_dict() for card in full_deck], len(full_deck))
        }

        # 초기 카드 분배
        self.deal_initial_cards()
        self.current_turn = 1

    def deal_initial_cards(self) -> None:
        self.hands = {
            player: sorted(
                [self.players[player].pop() for _ in range(CARDS_PER_HAND)],
                key=lambda card: (RANKS.index(card['rank']), SUITS.index(card['suit'])),
                reverse=True
            ) for player in self.players
        }
        self.calculate_all_scores()

    def calculate_all_scores(self) -> None:
        self.scores = {
            player: self.calculate_score(cards) 
            for player, cards in self.hands.items()
        }

    def calculate_score(self, cards: List[dict]) -> Tuple[int, str, int, int]:
        hand_analyzer = HandAnalyzer(cards)
        return hand_analyzer.analyze()

    def discard_cards(self, discard_indices: List[int]) -> None:
        if not discard_indices:
            self.next_turn()
            return

        for player, hand in self.hands.items():
            if player == 'Computer':
                continue

            # 카드 교체
            new_cards = []
            for index in sorted(discard_indices, reverse=True):
                if 0 <= index < len(hand):
                    hand.pop(index)
                    new_cards.append(self.players[player].pop())
            hand.extend(new_cards)
            
            # 핸드 정렬
            hand.sort(
                key=lambda card: (RANKS.index(card['rank']), SUITS.index(card['suit'])),
                reverse=True
            )

            # 새로운 점수로 업데이트 (무조건 새로운 족보 적용)
            self.scores[player] = self.calculate_score(hand)

        self.next_turn()

    def update_scores(self) -> None:
        for player, cards in self.hands.items():
            new_score = self.calculate_score(cards)
            current_score = self.scores.get(player, (0, '', 0, 0))
            
            if new_score[0] > current_score[0]:
                self.scores[player] = new_score

    def next_turn(self) -> None:
        if self.current_turn < self.max_turns:
            self.current_turn += 1
        else:
            self.determine_winner()

    def determine_winner(self) -> None:
        player_score = self.scores['Player 1'][0]
        computer_score = self.scores['Computer'][0]
        
        if player_score > computer_score:
            self.winner = 'Player 1'
        elif player_score < computer_score:
            self.winner = 'Computer'
        else:
            self.winner = 'Draw'
        self.current_turn = None

class HandAnalyzer:
    def __init__(self, cards: List[dict]):
        self.cards = cards
        self.rank_count = {}
        self.suit_count = {}
        self.total_rank_value = 0
        self.sorted_ranks = []
        self.analyze_cards()

    def analyze_cards(self) -> None:
        for card in self.cards:
            rank = card['rank']
            suit = card['suit']
            self.total_rank_value += RANK_VALUES[rank]
            
            self.rank_count[rank] = self.rank_count.get(rank, 0) + 1
            self.suit_count[suit] = self.suit_count.get(suit, 0) + 1

        self.sorted_ranks = sorted(RANK_VALUES[rank] for rank in self.rank_count.keys())

    def analyze(self) -> Tuple[int, str, int, int]:
        for hand_type, multiplier in HAND_RANKINGS.items():
            if hasattr(self, f'is_{hand_type.lower().replace(" ", "_")}'):
                check_method = getattr(self, f'is_{hand_type.lower().replace(" ", "_")}')
                if check_method():
                    return (self.total_rank_value * multiplier, hand_type, 
                           self.total_rank_value, multiplier)
        
        return (self.total_rank_value, 'High Card', self.total_rank_value, 1)

    def is_royal_flush(self) -> bool:
        return (any(count >= 5 for count in self.suit_count.values()) and
                set(['10', 'Jack', 'Queen', 'King', 'Ace']).issubset(self.rank_count.keys()))

    def is_straight_flush(self) -> bool:
        return (any(count >= 5 for count in self.suit_count.values()) and
                self.is_straight())

    def is_four_of_a_kind(self) -> bool:
        return 4 in self.rank_count.values()

    def is_full_house(self) -> bool:
        return 3 in self.rank_count.values() and 2 in self.rank_count.values()

    def is_flush(self) -> bool:
        return any(count >= 5 for count in self.suit_count.values())

    def is_straight(self) -> bool:
        if len(self.sorted_ranks) < 5:
            return False
        
        # 중복 제거하고 정렬된 랭크 값들
        unique_ranks = sorted(set(self.sorted_ranks))
        
        # 5장 이상의 연속된 카드 찾기
        for i in range(len(unique_ranks) - 4):
            if all(unique_ranks[j+1] - unique_ranks[j] == 1 
                   for j in range(i, i + 4)):
                return True
            
        # A-2-3-4-5 스트레이트 체크 (Ace를 1로 사용)
        if set([14, 2, 3, 4, 5]).issubset(set(unique_ranks)):
            return True
        
        return False

    def is_three_of_a_kind(self) -> bool:
        return 3 in self.rank_count.values()

    def is_two_pair(self) -> bool:
        return sum(1 for count in self.rank_count.values() if count == 2) >= 2

    def is_pair(self) -> bool:
        return sum(1 for count in self.rank_count.values() if count == 2) == 1
