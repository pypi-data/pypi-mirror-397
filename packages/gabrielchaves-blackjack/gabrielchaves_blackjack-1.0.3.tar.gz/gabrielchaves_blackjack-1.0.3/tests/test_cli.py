import pytest
import runpy
from unittest.mock import patch
from blackjack import cli


# =========================
#   clear_screen
# =========================
def test_clear_screen_runs_without_error():
  """
  clear_screen should execute without throwing an exception,
  regardless of the operating system.
  """
  cli.clear_screen()
  assert True


# =========================
#   print_welcome
# =========================
def test_print_welcome_outputs_text(capsys):
  with patch("blackjack.cli.wait_for_enter") as mocked_wait:
    mocked_wait.return_value = None  # Simulates pressing ENTER
    cli.print_welcome()
  
  captured = capsys.readouterr().out
  assert "WELCOME TO BLACKJACK" in captured
  assert "Rules:" in captured
  assert "Betting:" in captured


# =========================
#   print_game_over
# =========================
@pytest.mark.parametrize(
  "chips_won, expected",
  [
      (50, "Great job!"),
      (-20, "Better luck next time"),
      (0, "broke even"),
  ],
)
def test_print_game_over_variations(chips_won, expected, capsys):
  """
  print_game_over should display the correct message
  depending on the final result.    
  """
  cli.print_game_over(chips_won)

  output = capsys.readouterr().out
  assert expected.lower() in output.lower()
  assert "🅶🅰🅼🅴 🅾🆅🅴🆁" in output