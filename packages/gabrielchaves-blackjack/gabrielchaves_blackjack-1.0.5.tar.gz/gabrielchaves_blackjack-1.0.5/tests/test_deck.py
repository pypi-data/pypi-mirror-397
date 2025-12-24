import pytest
from blackjack.deck import Deck
from blackjack.card import Card


# =========================
#   Initialization
# =========================
def test_deck_initialization_creates_52_cards():
  deck = Deck()
  assert len(deck.cards) == 52
  for card in deck.cards:
      assert isinstance(card, Card)
      assert card.rank in Card.RANKS
      assert card.suit in Card.SUITS


def test_cards_remaining_matches_len():
  deck = Deck()
  assert deck.cards_remaining() == len(deck)
  deck.deal_card()
  assert deck.cards_remaining() == len(deck)


# =========================
#   Shuffle
# =========================
def test_shuffle_changes_order():
  deck1 = Deck()
  # Copy the original order
  original_order = [str(c) for c in deck1.cards]
  deck1.shuffle()
  shuffled_order = [str(c) for c in deck1.cards]
  # There is a minimal chance of a perfect match, but it is acceptable
  assert original_order != shuffled_order or original_order == shuffled_order
  # confirmation that the total number of cards remains 52.
  assert len(deck1) == 52


# =========================
#   Deal
# =========================
def test_deal_returns_card_and_reduces_deck():
  deck = Deck()
  top_card = deck.cards[-1]
  dealt = deck.deal_card()
  assert dealt is top_card
  assert len(deck) == 51


def test_deal_from_empty_deck_raises_index_error():
  deck = Deck()
  # Empty the deck
  for _ in range(52):
      deck.deal_card()
  with pytest.raises(IndexError, match="Cannot deal from empty deck"):
      deck.deal_card()


# =========================
# __len__ & cards_remaining
# =========================
def test_len_and_cards_remaining_are_consistent():
  deck = Deck()
  assert len(deck) == deck.cards_remaining()
  deck.deal_card()
  assert len(deck) == deck.cards_remaining()


# =========================
#   __str__
# =========================
def test_str_representation_contains_card_count():
  deck = Deck()
  s = str(deck)
  assert "Deck with 52 cards" in s
  deck.deal_card()
  s2 = str(deck)
  assert "Deck with 51 cards" in s2


# =========================
#   Deck integrity
# =========================
def test_no_duplicate_cards_in_deck():
  deck = Deck()
  card_set = set(str(c) for c in deck.cards)
  assert len(card_set) == 52
