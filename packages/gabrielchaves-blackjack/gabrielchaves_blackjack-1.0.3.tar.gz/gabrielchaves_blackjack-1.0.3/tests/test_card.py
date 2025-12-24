import pytest

from blackjack.card import Card


# ===========================
# Construction and validation
# ===========================
@pytest.mark.parametrize("rank", Card.RANKS)
@pytest.mark.parametrize("suit", Card.SUITS)
def test_card_creation_valid(rank, suit):
  card = Card(rank, suit)
  assert card.rank == rank
  assert card.suit == suit


def test_invalid_rank_raises_value_error():
  with pytest.raises(ValueError, match="Invalid rank"):
      Card("1", "♠")


def test_invalid_suit_raises_value_error():
  with pytest.raises(ValueError, match="Invalid suit"):
      Card("A", "X")


# =======================
#   Card values
# =======================
@pytest.mark.parametrize(
  "rank, expected",
  [
      ("2", 2),
      ("5", 5),
      ("10", 10),
      ("J", 10),
      ("Q", 10),
      ("K", 10),
      ("A", 11),
  ],
)
def test_card_value(rank, expected):
  card = Card(rank, "♣")
  assert card.value == expected


# =======================
#   ASCII Art
# =======================
def test_ascii_art_structure():
  card = Card("A", "♠")
  art = card.get_ascii_art()

  assert isinstance(art, list)
  assert len(art) == 7
  for line in art:
      assert isinstance(line, str)
      assert len(line) == 11


def test_ascii_art_contains_rank_and_suit():
  card = Card("K", "♥")
  art = card.get_ascii_art()

  joined = "\n".join(art)
  assert "K" in joined
  assert "♥" in joined


def test_ascii_art_alignment_single_digit():
  card = Card("7", "♦")
  art = card.get_ascii_art()

  assert art[1].startswith("│7 ")
  assert art[5].endswith("7 │")


def test_ascii_art_alignment_two_digits():
  card = Card("10", "♣")
  art = card.get_ascii_art()

  assert art[1].startswith("│10")
  assert art[5].endswith("10│")


# =======================
#   Hidden card
# =======================
def test_hidden_card_ascii_structure():
  art = Card.get_hidden_card_ascii()

  assert isinstance(art, list)
  assert len(art) == 7
  for line in art:
      assert len(line) == 11


def test_hidden_card_ascii_content():
  art = Card.get_hidden_card_ascii()

  assert art[0] == "┌─────────┐"
  assert art[-1] == "└─────────┘"
  for line in art[1:-1]:
      assert "░" in line


def test_hidden_card_is_independent_of_instance():
  card = Card("A", "♠")
  art = card.get_hidden_card_ascii()

  assert art == Card.get_hidden_card_ascii()


# =========================
# __str__ and __repr__
# =========================
def test_str_representation():
  card = Card("Q", "♣")
  assert str(card) == "Q♣"


def test_repr_representation():
  card = Card("10", "♦")
  repr_str = repr(card)

  assert repr_str == "Card(rank='10', suit='♦')"
  assert "Card" in repr_str
  assert "rank='10'" in repr_str
  assert "suit='♦'" in repr_str
