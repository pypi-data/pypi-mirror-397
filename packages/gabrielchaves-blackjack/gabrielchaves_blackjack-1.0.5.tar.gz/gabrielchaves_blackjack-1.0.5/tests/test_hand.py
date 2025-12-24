import pytest
from blackjack.hand import Hand
from blackjack.card import Card


# =========================
#   Initialization
# =========================
def test_hand_initialization():
  hand = Hand()
  assert isinstance(hand.cards, list)
  assert len(hand.cards) == 0
  assert hand.get_value() == 0
  assert not hand.is_bust()
  assert not hand.is_blackjack()


# =========================
#   Adding cards
# =========================
def test_add_card_increases_length_and_value():
  hand = Hand()
  card1 = Card("5", "♠")
  card2 = Card("K", "♦")
  
  hand.add_card(card1)
  assert len(hand) == 1
  assert hand.get_value() == 5
  
  hand.add_card(card2)
  assert len(hand) == 2
  assert hand.get_value() == 15


# =========================
#   Bust detection
# =========================
def test_is_bust_true_and_false():
  hand = Hand()
  hand.add_card(Card("K", "♠"))
  hand.add_card(Card("Q", "♦"))
  assert not hand.is_bust()
  
  hand.add_card(Card("5", "♥"))
  assert hand.is_bust()


# =========================
#   Blackjack detection
# =========================
def test_is_blackjack_true_and_false():
  hand = Hand()
  hand.add_card(Card("A", "♠"))
  hand.add_card(Card("K", "♦"))
  assert hand.is_blackjack()
  
  hand2 = Hand()
  hand2.add_card(Card("A", "♠"))
  hand2.add_card(Card("9", "♦"))
  assert not hand2.is_blackjack()
  
  hand3 = Hand()
  hand3.add_card(Card("A", "♠"))
  hand3.add_card(Card("K", "♦"))
  hand3.add_card(Card("5", "♣"))
  assert not hand3.is_blackjack()


# =========================
#   Clear hand
# =========================
def test_clear_hand_resets_cards():
  hand = Hand()
  hand.add_card(Card("5", "♠"))
  hand.add_card(Card("K", "♦"))
  assert len(hand) == 2
  hand.clear()
  assert len(hand) == 0
  assert hand.get_value() == 0
  assert not hand.is_bust()
  assert not hand.is_blackjack()


# =========================
#   String representation
# =========================
def test_hand_str_returns_expected_format():
  hand = Hand()
  c1 = Card("A", "♠")
  c2 = Card("10", "♦")
  hand.add_card(c1)
  hand.add_card(c2)
  s = str(hand)
  assert str(c1) in s
  assert str(c2) in s
  assert f"Value: {hand.get_value()}" in s


# =========================
#   Length of hand
# =========================
def test_len_returns_number_of_cards():
  hand = Hand()
  assert len(hand) == 0
  hand.add_card(Card("5", "♠"))
  assert len(hand) == 1
  hand.add_card(Card("K", "♦"))
  assert len(hand) == 2
