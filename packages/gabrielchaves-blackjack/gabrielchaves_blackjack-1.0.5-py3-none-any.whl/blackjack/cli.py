"""
CLI module - Command-line interface for the game with ASCII display and betting.
"""

import os
import sys
import platform
from .game import BlackJackGame
from .input_handler import get_filtered_input, wait_for_enter

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def clear_screen():
  """
  Clear the terminal screen.
  """
  if platform.system() == "Windows":
    os.system("cls")
  else:
    os.system("clear")

def print_welcome() -> None:
  """
  Print welcome message.
  """
  clear_screen()
  print("\n" + "="*80)
  print("♠♥♦♣  WELCOME TO BLACKJACK  ♣♦♥♠".center(80))
  print("="*80)
  print("\nRules:")
  print("  • Get as close to 21 as possible without going over")
  print("  • Face cards (J, Q, K) are worth 10")
  print("  • Aces are worth 11")
  print("\nBetting:")
  print("  • You start with 200 chips")
  print("  • Available bets: 1, 5, 10, 25, or 50 chips")
  print("  • Win your bet back on a win, lose your bet on a loss")
  print("  • Game over when you run out of chips!")
  print("\n" + "="*80 + "\n")
  # Use wait_for_enter to block pasting and only accept ENTER
  wait_for_enter("Press ENTER to start playing...")

def print_game_over(chips_won: int) -> None:
  """
  Print game over message.
  
  Args:
    chips_won: Total chips won/lost (positive or negative)
  """
  clear_screen()
  print("\n" + "="*80)
  print("* 🅶🅰🅼🅴 🅾🆅🅴🆁 - OUT OF CHIPS! *".center(80))
  print("="*80)
  print("")
  
  if chips_won > 0:
    print(f".⋅˚₊‧ 🜲 ‧₊˚ ⋅ Great job! You won {chips_won} chips total!".center(80))
  elif chips_won < 0:
    print(f"You lost all chips. Better luck next time! •︵•".center(80))
  else:
    print("You broke even. Not bad!".center(80))
  
  print("")
  print("="*80 + "\n")

def main() -> None:
  """
  Main entry point for the CLI game.
  """
  print_welcome()

  while True:
    game = BlackJackGame()
    starting_chips = game.player.chips
    
    # Play rounds until player runs out of chips or quits
    while game.player.has_chips():
      continue_playing = game.play_round()
      
      if not continue_playing:
        # Player chose to quit
        clear_screen()
        print("\n" + "="*80)
        print(" Thanks for playing!".center(80))
        print(f"Final Chips: {game.player.chips} ⛁".center(80))
        chips_change = game.player.chips - starting_chips
        if chips_change > 0:
          print(f"You won {chips_change} chips! $ˎˊ˗".center(80))
        elif chips_change < 0:
          print(f"You lost {abs(chips_change)} chips.".center(80))
        print("="*80 + "\n")
        return
      
      # Check if player still has chips
      if not game.player.has_chips():
        chips_change = game.player.chips - starting_chips
        print_game_over(chips_change)
        break
      
      # Ask to play another round
      response = get_filtered_input("\n🃜🃚🃖🃁🂭🂺 Play another round? [Y/N] ", "YN", use_simple=False)
      if response != 'Y':
        clear_screen()
        print("\n" + "="*80)
        print(" Thanks for playing!".center(80))
        print(f"Final Chips: {game.player.chips} ⛀⛁".center(80))
        chips_change = game.player.chips - starting_chips
        if chips_change > 0:
          print(f"You won {chips_change} chips!⛃".center(80))
        elif chips_change < 0:
          print(f"You lost {abs(chips_change)} chips.".center(80))
        print("="*80 + "\n")
        return
    
    # Player ran out of chips - ask if they want to start over
    response = get_filtered_input("\n⟳ Start a new game with 200 chips? [Y/N] ", "YN")
    if response != 'Y':
      clear_screen()
      print("\n" + "="*80)
      print("Thanks for playing! Goodbye!".center(80))
      print("="*80 + "\n")
      return

if __name__ == "__main__":
  main()