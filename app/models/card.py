"""
카드 관련 클래스 정의
"""
from dataclasses import dataclass
from typing import Dict
from config.settings import RANKS, SUITS, RANK_VALUES

@dataclass
class Card:
    """카드 클래스"""
    suit: str
    rank: str

    def __post_init__(self):
        """유효성 검사"""
        if self.suit not in SUITS:
            raise ValueError(f"Invalid suit: {self.suit}")
        if self.rank not in RANKS:
            raise ValueError(f"Invalid rank: {self.rank}")

    @property
    def value(self) -> int:
        """카드의 숫자 값을 반환"""
        return RANK_VALUES[self.rank]

    def to_dict(self) -> Dict[str, str]:
        """카드를 딕셔너리로 변환"""
        return {
            'suit': self.suit,
            'rank': self.rank
        } 