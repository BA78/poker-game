"""
AI 관련 클래스 정의
"""
from typing import List
from app.models.card import Card
from app.models.hand import Hand

class PokerAI:
    """포커 AI 클래스"""
    def __init__(self, hand: List[Card]):
        self.hand = hand
        self.hand_analyzer = Hand(hand)

    def decide_cards_to_discard(self) -> List[int]:
        """버릴 카드 결정"""
        score = self.hand_analyzer.analyze()
        potential = self.hand_analyzer.get_hand_potential()
        
        # 이미 좋은 패를 가지고 있으면 유지
        if score[3] >= 7:  # Full House 이상
            return []

        cards_to_discard = []
        
        # 포카드에 가까운 경우
        if score[3] == 8:  # Four of a Kind
            rank_to_keep = next(rank for rank, count in self.hand_analyzer._rank_count.items() 
                              if count == 4)
            return [i for i, card in enumerate(self.hand) 
                   if card.rank != rank_to_keep]

        # 플러시에 가까운 경우
        if potential['flush_potential']:
            main_suit = max(self.hand_analyzer._suit_count.items(), 
                          key=lambda x: x[1])[0]
            return [i for i, card in enumerate(self.hand) 
                   if card.suit != main_suit]

        # 스트레이트에 가까운 경우
        if potential['straight_potential']:
            values = sorted(set(card.value for card in self.hand))
            consecutive = self._find_consecutive_values(values)
            return [i for i, card in enumerate(self.hand) 
                   if card.value not in consecutive]

        # 트리플이 있는 경우
        if potential['three_of_kind']:
            rank_to_keep = next(rank for rank, count in self.hand_analyzer._rank_count.items() 
                              if count == 3)
            return [i for i, card in enumerate(self.hand) 
                   if card.rank != rank_to_keep]

        # 투페어가 있는 경우
        if potential['pairs'] >= 2:
            pair_ranks = [rank for rank, count in self.hand_analyzer._rank_count.items() 
                         if count == 2]
            return [i for i, card in enumerate(self.hand) 
                   if card.rank not in pair_ranks]

        # 원페어가 있는 경우
        if potential['pairs'] == 1:
            pair_rank = next(rank for rank, count in self.hand_analyzer._rank_count.items() 
                           if count == 2)
            return [i for i, card in enumerate(self.hand) 
                   if card.rank != pair_rank]

        # 아무것도 없는 경우, 가장 높은 카드 하나만 남기고 모두 교체
        sorted_indices = sorted(range(len(self.hand)), 
                              key=lambda i: self.hand[i].value,
                              reverse=True)
        return sorted_indices[1:]

    def _find_consecutive_values(self, values: List[int]) -> List[int]:
        """연속된 숫자들 찾기"""
        best_consecutive = []
        current_consecutive = [values[0]]
        
        for i in range(1, len(values)):
            if values[i] - values[i-1] <= 2:  # 2 이하의 차이는 연속으로 간주
                current_consecutive.append(values[i])
            else:
                if len(current_consecutive) > len(best_consecutive):
                    best_consecutive = current_consecutive[:]
                current_consecutive = [values[i]]
        
        if len(current_consecutive) > len(best_consecutive):
            best_consecutive = current_consecutive
            
        return best_consecutive 