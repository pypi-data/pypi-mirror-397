import pytest
from blackjack.game import BlackJackGame
from blackjack.card import Card
from blackjack.player import Hand


# =========================
#   Initialization
# =========================
def test_game_initialization():
  game = BlackJackGame()
  assert hasattr(game, "deck")
  assert hasattr(game, "player")
  assert hasattr(game, "dealer")
  assert isinstance(game.deck, object)
  assert game.player.chips == 200
  assert not game.game_over


# =========================
#   show_chips_info
# =========================
def test_show_chips_info_format():
  game = BlackJackGame()
  info = game.show_chips_info()
  assert "Your Chips" in info
  assert str(game.player.current_bet) in info


# =========================
#   setup_round
# =========================
def test_setup_round_deals_two_cards_each():
  game = BlackJackGame()
  game.setup_round()
  assert len(game.player.hand) == 2
  assert len(game.dealer.hand) == 2
  assert not game.game_over


# =========================
# show_initial_hands & show_all_hands
# =========================
def test_show_hands_output_contains_important_info():
  game = BlackJackGame()
  game.setup_round()
  initial = game.show_initial_hands()
  all_hands = game.show_all_hands()
  
  # Should contain chip information.
  assert "Your Chips" in initial
  assert "Your Chips" in all_hands
  
  # Must contain suit symbols from some card (♠ ♥ ♦ ♣)
  suits = ["♠", "♥", "♦", "♣"]
  assert any(suit in initial for suit in suits)
  assert any(suit in all_hands for suit in suits)


# =========================
#   player_hit
# =========================
def test_player_hit_adds_card_and_returns_bust_message():
  game = BlackJackGame()
  game.setup_round()
  initial_hand_size = len(game.player.hand.cards)
  is_bust, message = game.player_hit()
  assert len(game.player.hand.cards) == initial_hand_size + 1
  assert isinstance(is_bust, bool)
  assert isinstance(message, str)
  assert "Your Chips" in message
  assert str(game.player.hand.cards[-1]) in message


# =========================
#   determine_winner
# =========================
def test_determine_winner_updates_chips_correctly():
  game = BlackJackGame()
  game.setup_round()

  # Artificial bust
  game.player.hand = Hand()
  game.player.hand.add_card(Card("K", "♠"))
  game.player.hand.add_card(Card("Q", "♠"))
  game.player.hand.add_card(Card("2", "♠"))
  game.player.current_bet = 10  # set bet

  result = game.determine_winner()
  assert "DEALER WINS" in result
  assert game.player.chips == 190  # 200 - 10

  # Player's victory
  game.player.hand = Hand()
  game.player.hand.add_card(Card("A", "♠"))
  game.player.hand.add_card(Card("K", "♠"))
  game.player.current_bet = 10
  
  game.dealer.hand = Hand()
  game.dealer.hand.add_card(Card("2", "♠"))

  result_win = game.determine_winner()
  assert "YOU WIN" in result_win
  assert game.player.chips == 200  # 190 + 10


# =========================
#   play_round
# =========================
def test_play_round_returns_false_when_quit(monkeypatch):
  """
  Test the play_round flow by simulating the player choosing to exit (Q) upon entering.
  We use monkeypatch (a lightweight form of mock) only here.
  """
  game = BlackJackGame()

  # Replace get_filtered_input to always return "Q"
  monkeypatch.setattr(
      "blackjack.game.get_filtered_input",
      lambda prompt, valid: "Q"
  )

  result = game.play_round()
  assert result is False
