"""
게임 설정 파일
"""

# 카드 관련 상수
SUITS = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14
}

# 게임 관련 상수
CARDS_PER_HAND = 7
MAX_TURNS = 5

# 족보 관련 상수
HAND_RANKINGS = [
    ('Royal Flush', 10),
    ('Straight Flush', 9),
    ('Four of a Kind', 8),
    ('Full House', 7),
    ('Flush', 6),
    ('Straight', 5),
    ('Three of a Kind', 4),
    ('Two Pair', 3),
    ('Pair', 2),
    ('High Card', 1)
] 