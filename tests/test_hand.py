import unittest
from app.models.card import Card
from app.models.hand import Hand

class TestHand(unittest.TestCase):
    
    def test_royal_flush(self):
        """로얄 플러시 테스트"""
        cards = [
            Card('Hearts', '10'),
            Card('Hearts', 'Jack'),
            Card('Hearts', 'Queen'),
            Card('Hearts', 'King'),
            Card('Hearts', 'Ace'),
            Card('Clubs', '2'),
            Card('Clubs', '3')
        ]
        hand = Hand(cards)
        self.assertTrue(hand.is_royal_flush())
        
    def test_straight_flush(self):
        """스트레이트 플러시 테스트"""
        cards = [
            Card('Spades', '5'),
            Card('Spades', '6'),
            Card('Spades', '7'),
            Card('Spades', '8'),
            Card('Spades', '9'),
            Card('Hearts', '2'),
            Card('Diamonds', '3')
        ]
        hand = Hand(cards)
        self.assertTrue(hand.is_straight_flush())
        self.assertFalse(hand.is_royal_flush())
        
    def test_four_of_a_kind(self):
        """포카드 테스트"""
        cards = [
            Card('Hearts', '8'),
            Card('Spades', '8'),
            Card('Diamonds', '8'),
            Card('Clubs', '8'),
            Card('Hearts', '3'),
            Card('Spades', '4'),
            Card('Clubs', '5')
        ]
        hand = Hand(cards)
        self.assertTrue(hand.is_four_of_a_kind())
        self.assertFalse(hand.is_full_house())
        
    def test_full_house(self):
        """풀하우스 테스트"""
        cards = [
            Card('Hearts', 'Queen'),
            Card('Diamonds', 'Queen'),
            Card('Clubs', 'Queen'),
            Card('Hearts', '2'),
            Card('Diamonds', '2'),
            Card('Clubs', '3'),
            Card('Spades', '4')
        ]
        hand = Hand(cards)
        self.assertTrue(hand.is_full_house())
        self.assertFalse(hand.is_four_of_a_kind())
        
    def test_flush(self):
        """플러시 테스트"""
        cards = [
            Card('Hearts', '2'),
            Card('Hearts', '5'),
            Card('Hearts', '7'),
            Card('Hearts', '9'),
            Card('Hearts', 'King'),
            Card('Clubs', '6'),
            Card('Diamonds', 'Ace')
        ]
        hand = Hand(cards)
        self.assertTrue(hand.is_flush())
        self.assertFalse(hand.is_straight())
        
    def test_low_straight(self):
        """A-2-3-4-5 스트레이트 테스트"""
        cards = [
            Card('Hearts', 'Ace'),
            Card('Diamonds', '2'),
            Card('Clubs', '3'),
            Card('Spades', '4'),
            Card('Hearts', '5'),
            Card('Clubs', '8'),
            Card('Spades', 'King')
        ]
        hand = Hand(cards)
        self.assertTrue(hand.is_straight())

if __name__ == '__main__':
    unittest.main()
