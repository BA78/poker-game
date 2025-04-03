from typing import Dict, List, Tuple
import random
from constants import *

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def to_dict(self) -> dict:
        return {'suit': self.suit, 'rank': self.rank}

class PokerAI:
    def __init__(self, hand, deck):
        self.hand = hand
        self.deck = deck
        self.current_score = None
        self.current_hand_type = None
        self.current_multiplier = None

    def analyze_hand(self):
        """현재 패 분석"""
        hand_analyzer = HandAnalyzer(self.hand)
        score, hand_type, total_value, multiplier = hand_analyzer.analyze()
        self.current_score = score
        self.current_hand_type = hand_type
        self.current_multiplier = multiplier
        return hand_type, multiplier

    def find_best_hand_potential(self):
        """현재 패의 잠재력 분석"""
        rank_count = {}
        suit_count = {}
        
        for card in self.hand:
            rank = card['rank']
            suit = card['suit']
            rank_count[rank] = rank_count.get(rank, 0) + 1
            suit_count[suit] = suit_count.get(suit, 0) + 1

        # 플러시 가능성 체크
        flush_potential = max(suit_count.values()) >= 4

        # 스트레이트 가능성 체크
        ranks = [RANK_VALUES[card['rank']] for card in self.hand]
        ranks.sort()
        straight_potential = False
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] <= 4:
                straight_potential = True
                break

        return {
            'pairs': len([count for count in rank_count.values() if count == 2]),
            'three_of_kind': any(count >= 3 for count in rank_count.values()),
            'flush_potential': flush_potential,
            'straight_potential': straight_potential
        }

    def decide_cards_to_discard(self):
        """버릴 카드 결정"""
        hand_type, multiplier = self.analyze_hand()
        potential = self.find_best_hand_potential()
        cards_to_discard = []

        # 로얄 스트레이트 플러시나 스트레이트 플러시인 경우만 카드를 유지
        if multiplier >= 9:
            return []

        # 포카드인 경우 나머지 한 장 교체
        if multiplier == 8:  # Four of a Kind
            rank_count = {}
            for card in self.hand:
                rank_count[card['rank']] = rank_count.get(card['rank'], 0) + 1
            four_rank = next(rank for rank, count in rank_count.items() if count == 4)
            return [card for card in self.hand if card['rank'] != four_rank]

        # 플러시에 가까운 경우
        if potential['flush_potential']:
            main_suit = max(((suit, sum(1 for card in self.hand if card['suit'] == suit))
                           for suit in set(card['suit'] for card in self.hand)),
                          key=lambda x: x[1])[0]
            cards_to_discard = [card for card in self.hand if card['suit'] != main_suit]
            return cards_to_discard

        # 스트레이트에 가까운 경우
        if potential['straight_potential']:
            ranks = sorted([RANK_VALUES[card['rank']] for card in self.hand])
            consecutive = self._find_consecutive_ranks(ranks)
            cards_to_discard = [card for card in self.hand 
                              if RANK_VALUES[card['rank']] not in consecutive]
            return cards_to_discard

        # 트리플이 있는 경우
        if potential['three_of_kind']:
            rank_count = {}
            for card in self.hand:
                rank_count[card['rank']] = rank_count.get(card['rank'], 0) + 1
            triple_rank = next(rank for rank, count in rank_count.items() if count >= 3)
            return [card for card in self.hand if card['rank'] != triple_rank]

        # 투페어가 있는 경우
        if potential['pairs'] >= 2:
            rank_count = {}
            for card in self.hand:
                rank_count[card['rank']] = rank_count.get(card['rank'], 0) + 1
            pair_ranks = [rank for rank, count in rank_count.items() if count == 2]
            return [card for card in self.hand if card['rank'] not in pair_ranks]

        # 원페어가 있는 경우
        if potential['pairs'] == 1:
            rank_count = {}
            for card in self.hand:
                rank_count[card['rank']] = rank_count.get(card['rank'], 0) + 1
            pair_rank = next(rank for rank, count in rank_count.items() if count == 2)
            return [card for card in self.hand if card['rank'] != pair_rank]

        # 아무것도 없는 경우, 가장 높은 카드 하나만 남기고 모두 교체
        sorted_hand = sorted(self.hand, 
                           key=lambda x: RANK_VALUES[x['rank']], 
                           reverse=True)
        return sorted_hand[1:]

    def _find_consecutive_ranks(self, ranks):
        """연속된 숫자들 찾기"""
        best_consecutive = []
        current_consecutive = [ranks[0]]
        
        for i in range(1, len(ranks)):
            if ranks[i] - ranks[i-1] <= 2:  # 2 이하의 차이는 연속으로 간주
                current_consecutive.append(ranks[i])
            else:
                if len(current_consecutive) > len(best_consecutive):
                    best_consecutive = current_consecutive[:]
                current_consecutive = [ranks[i]]
        
        if len(current_consecutive) > len(best_consecutive):
            best_consecutive = current_consecutive
            
        return best_consecutive

class PokerGame:
    def __init__(self):
        self.reset_game()

    def reset_game(self) -> None:
        self.players = {}
        self.hands = {}
        self.scores = {}
        self.previous_scores = {}  # 이전 턴의 점수를 저장
        self.previous_hands = {}   # 이전 턴의 핸드를 저장
        self.card_changes = {}     # 카드 변경 내역을 저장
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

            # 현재 점수와 족보 저장
            current_score, current_hand_type, current_total_value, current_multiplier = self.scores[player]

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

            # 새로운 점수 계산
            new_score, new_hand_type, new_total_value, new_multiplier = self.calculate_score(hand)

            # 더 높은 배율의 족보를 유지
            if current_multiplier > new_multiplier:
                self.scores[player] = (current_score, current_hand_type, current_total_value, current_multiplier)
            else:
                self.scores[player] = (new_score, new_hand_type, new_total_value, new_multiplier)

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
            
            # 새로운 턴 시작 시 card_changes 초기화
            self.card_changes = {}
            
            # 컴퓨터의 턴 처리
            self._handle_computer_turn()
        else:
            self.determine_winner()

    def _handle_computer_turn(self) -> None:
        """컴퓨터의 턴 처리"""
        # 현재 점수를 이전 점수로 저장
        self.previous_scores = {
            'Computer': self.scores['Computer'],
            'Player 1': self.scores['Player 1']
        }

        computer_hand = self.hands['Computer']
        ai = PokerAI(computer_hand, self.players['Computer'])
        cards_to_discard = ai.decide_cards_to_discard()

        if cards_to_discard:
            # 선택된 카드 버리기
            for card in cards_to_discard:
                computer_hand.remove(card)
                new_card = self.players['Computer'].pop()
                computer_hand.append(new_card)

            # 핸드 정렬
            computer_hand.sort(
                key=lambda card: (RANKS.index(card['rank']), SUITS.index(card['suit'])),
                reverse=True
            )

            # 카드를 교체했다면 무조건 새로운 점수로 업데이트
            self.scores['Computer'] = self.calculate_score(computer_hand)

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
