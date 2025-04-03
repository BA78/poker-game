"""
플레이어 관련 클래스 정의
"""
from typing import List, Dict, Tuple, Optional
from app.models.card import Card
from app.models.hand import Hand

class Player:
    """플레이어 클래스"""
    def __init__(self, name: str):
        self.name = name
        self.deck: List[Card] = []
        self.hand: List[Card] = []
        self.score: Optional[Tuple[int, str, int, int]] = None
        self.previous_score: Optional[Tuple[int, str, int, int]] = None
        self.card_changes: Dict[str, List[Dict[str, str]]] = {
            'discarded': [],
            'drawn': []
        }

    def draw_initial_cards(self, num_cards: int) -> None:
        """초기 카드를 뽑음"""
        self.hand = [self.deck.pop() for _ in range(num_cards)]
        self._sort_hand()
        self._calculate_score()
        self.card_changes = {'discarded': [], 'drawn': []}

    def discard_cards(self, indices: List[int]) -> None:
        """카드를 버리고 새로 뽑음"""
        self.previous_score = self.score
        self.card_changes = {'discarded': [], 'drawn': []}
        
        # 카드 버리기
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.hand):
                discarded_card = self.hand.pop(index)
                self.card_changes['discarded'].append(discarded_card.to_dict())
                new_card = self.deck.pop()
                self.hand.append(new_card)
                self.card_changes['drawn'].append(new_card.to_dict())
        
        self._sort_hand()
        self._calculate_score()

    def _sort_hand(self) -> None:
        """패를 정렬"""
        self.hand.sort(key=lambda card: (card.value, card.suit), reverse=True)

    def _calculate_score(self) -> None:
        """점수 계산"""
        hand_analyzer = Hand(self.hand)
        self.score = hand_analyzer.analyze()

    def get_hand_dict(self) -> List[Dict[str, str]]:
        """패를 딕셔너리 리스트로 변환"""
        return [card.to_dict() for card in self.hand] 