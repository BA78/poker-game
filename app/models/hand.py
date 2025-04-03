"""
패 분석 관련 클래스 정의
"""
from typing import List, Dict, Tuple, Set
from collections import Counter
from .card import Card
from config.settings import HAND_RANKINGS

class Hand:
    """패 분석 클래스"""
    def __init__(self, cards: List[Card]):
        self.cards = cards
        self._rank_count = Counter(card.rank for card in cards)
        self._suit_count = Counter(card.suit for card in cards)
        self._total_value = sum(card.value for card in cards)
        self._sorted_values = sorted(card.value for card in cards)

    def analyze(self) -> Tuple[int, str, int, int]:
        """패의 족보와 점수를 분석"""
        # High Card를 제외한 모든 족보 체크
        for hand_type, multiplier in HAND_RANKINGS[:-1]:  # High Card 제외
            check_method = getattr(self, f'is_{hand_type.lower().replace(" ", "_")}')
            if check_method():
                return (self._total_value * multiplier, hand_type, 
                       self._total_value, multiplier)
        
        # 어떤 족보도 없으면 High Card 반환
        return (self._total_value, 'High Card', self._total_value, 1)

    def is_royal_flush(self) -> bool:
        """로얄 플러시 체크"""
        royal_ranks = {'10', 'Jack', 'Queen', 'King', 'Ace'}
        return (any(count >= 5 for count in self._suit_count.values()) and
                royal_ranks.issubset(self._rank_count.keys()))

    def is_straight_flush(self) -> bool:
        """스트레이트 플러시 체크"""
        return (any(count >= 5 for count in self._suit_count.values()) and
                self.is_straight())

    def is_four_of_a_kind(self) -> bool:
        """포카드 체크"""
        return 4 in self._rank_count.values()

    def is_full_house(self) -> bool:
        """풀하우스 체크"""
        # 각 랭크별 카드 개수를 리스트로 변환
        counts = list(self._rank_count.values())
        # 트리플이 2개인 경우 (예: QQQ 999)
        if counts.count(3) == 2:
            return True
        # 트리플 1개와 페어 1개 이상인 경우 (예: QQQ 99)
        return counts.count(3) == 1 and counts.count(2) >= 1

    def is_flush(self) -> bool:
        """플러시 체크"""
        return any(count >= 5 for count in self._suit_count.values())

    def is_straight(self) -> bool:
        """스트레이트 체크"""
        if len(self._sorted_values) < 5:
            return False
        
        unique_values = sorted(set(self._sorted_values))
        
        # 일반적인 스트레이트 체크
        for i in range(len(unique_values) - 4):
            if all(unique_values[j+1] - unique_values[j] == 1 
                   for j in range(i, i + 4)):
                return True
            
        # A-2-3-4-5 스트레이트 체크
        if set([14, 2, 3, 4, 5]).issubset(set(unique_values)):
            return True
        
        return False

    def is_three_of_a_kind(self) -> bool:
        """트리플 체크"""
        # 풀하우스가 아니면서 트리플이 있는 경우만 체크
        counts = list(self._rank_count.values())
        return counts.count(3) == 1 and counts.count(2) == 0

    def is_two_pair(self) -> bool:
        """투페어 체크"""
        return sum(1 for count in self._rank_count.values() if count == 2) >= 2

    def is_pair(self) -> bool:
        """원페어 체크"""
        return 2 in self._rank_count.values()

    def get_hand_potential(self) -> Dict[str, bool]:
        """현재 패의 잠재력 분석"""
        # 카드가 없는 경우 처리
        if not self.cards:
            return {
                'pairs': 0,
                'three_of_kind': False,
                'flush_potential': False,
                'straight_potential': False
            }
            
        # suit_count가 비어있는 경우를 위한 안전한 처리
        max_suit_count = max(self._suit_count.values()) if self._suit_count else 0
        
        return {
            'pairs': len([count for count in self._rank_count.values() if count == 2]),
            'three_of_kind': 3 in self._rank_count.values(),
            'flush_potential': max_suit_count >= 4,
            'straight_potential': self._has_straight_potential()
        }

    def _has_straight_potential(self) -> bool:
        """스트레이트 가능성 체크"""
        values = sorted(set(self._sorted_values))
        for i in range(len(values) - 3):
            if values[i+3] - values[i] <= 4:
                return True
        return False 