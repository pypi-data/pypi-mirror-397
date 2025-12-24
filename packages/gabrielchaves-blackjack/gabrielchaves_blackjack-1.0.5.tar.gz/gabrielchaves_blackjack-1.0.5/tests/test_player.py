import pytest
from blackjack.player import Player, Dealer
from blackjack.hand import Hand
from blackjack.card import Card


# =========================
# Player Initialization
# =========================
def test_player_initialization():
  p = Player("Alice", chips=150)
  assert p.name == "Alice"
  assert p.chips == 150
  assert isinstance(p.hand, Hand)
  assert p.current_bet == 0


def test_dealer_initialization():
  d = Dealer()
  assert d.name == "Dealer"
  assert d.chips == 0
  assert isinstance(d.hand, Hand)


# =========================
# Betting logic
# =========================
def test_place_bet_valid_and_invalid():
  p = Player("Alice", chips=100)
  # Valid bet
  assert p.place_bet(50) is True
  assert p.current_bet == 50
  # Bet too high
  assert p.place_bet(200) is False
  # Bet zero or negative
  assert p.place_bet(0) is False
  assert p.place_bet(-10) is False


def test_win_lose_push_bet():
  p = Player("Alice", chips=100)
  p.place_bet(20)
  p.win_bet()
  assert p.chips == 120
  assert p.current_bet == 0

  p.place_bet(50)
  p.lose_bet()
  assert p.chips == 70
  assert p.current_bet == 0

  p.place_bet(10)
  p.push_bet()
  assert p.chips == 70
  assert p.current_bet == 0


def test_has_chips_and_can_bet():
  p = Player("Alice", chips=10)
  assert p.has_chips() is True
  assert p.can_bet(5) is True
  assert p.can_bet(15) is False


# =========================
# Hand manipulation
# =========================
def test_receive_card_and_clear_hand():
  p = Player("Alice")
  c1 = Card("A", "♠")
  c2 = Card("K", "♣")
  p.receive_card(c1)
  p.receive_card(c2)
  assert len(p.hand.cards) == 2
  assert p.hand.get_value() == c1.value + c2.value
  p.clear_hand()
  assert len(p.hand.cards) == 0


def test_is_bust_and_hand_value():
  p = Player("Alice")
  p.receive_card(Card("K", "♠"))
  p.receive_card(Card("Q", "♣"))
  p.receive_card(Card("2", "♦"))
  assert p.is_bust() is True
  assert p.get_hand_value() == 22


def test_show_hand_ascii_and_str_contains_cards():
  p = Player("Alice")
  c1 = Card("A", "♠")
  c2 = Card("9", "♦")
  p.receive_card(c1)
  p.receive_card(c2)
  
  ascii_str = p.show_hand_ascii()
  # Checar valor total da mão
  assert f"Value: {c1.value + c2.value}" in ascii_str
  # Checar que símbolos dos cards estão na arte
  assert "A" in ascii_str
  assert "9" in ascii_str
  assert "♠" in ascii_str
  assert "♦" in ascii_str

  str_hand = p.show_hand()
  # show_hand simula str(card), então este assert funciona
  assert str(c1) in str_hand
  assert str(c2) in str_hand


def test_show_hand_with_hidden_card():
  p = Player("Alice")
  c1 = Card("A", "♠")
  c2 = Card("9", "♦")
  p.receive_card(c1)
  p.receive_card(c2)
  hidden = p.show_hand(hide_first=True)
  assert "[Hidden]" in hidden
  # Value only counts visible card
  assert f"{c2.value}" in hidden


# =========================
# Dealer strategy should_hit
# =========================
def test_dealer_should_hit_hard_and_soft():
  d = Dealer()
  
  # Hard hand < 17
  d.hand.add_card(Card("7", "♠"))
  d.hand.add_card(Card("9", "♣"))
  assert d.should_hit() is True

  # Hard hand >= 17
  d.hand.clear()
  d.hand.add_card(Card("10", "♠"))
  d.hand.add_card(Card("7", "♣"))
  assert d.should_hit() is False

  # Soft hand A+5
  d.hand.clear()
  d.hand.add_card(Card("A", "♠"))
  d.hand.add_card(Card("5", "♣"))
  assert d.should_hit() is True

  # Soft hand A+9
  d.hand.clear()
  d.hand.add_card(Card("A", "♠"))
  d.hand.add_card(Card("9", "♣"))
  assert d.should_hit() is False


# =========================
# Dealer strategy multi-card hands
# =========================
def test_dealer_should_hit_multiple_cards():
  d = Dealer()
  d.hand.add_card(Card("10", "♠"))
  d.hand.add_card(Card("6", "♣"))
  d.hand.add_card(Card("2", "♦"))  # total 18
  # Should stand because 18 >= 17
  assert d.should_hit() is False
  # Bust case
  d.hand.clear()
  d.hand.add_card(Card("10", "♠"))
  d.hand.add_card(Card("9", "♣"))
  d.hand.add_card(Card("5", "♦"))  # total 24
  assert d.should_hit() is False
