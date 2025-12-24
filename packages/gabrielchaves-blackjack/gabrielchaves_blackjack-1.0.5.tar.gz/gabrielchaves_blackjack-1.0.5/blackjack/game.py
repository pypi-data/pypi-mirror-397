"""
Game module - Main game logic and flow with ASCII display and betting system.
"""

import os
import platform
from .deck import Deck
from .player import Player, Dealer
from .input_handler import get_filtered_input

def clear_screen():
  """
  Clear the terminal screen.
  """
  if platform.system() == "Windows":
    os.system("cls")
  else:
    os.system("clear")

class BlackJackGame:
  """
  Main blackjack game controller with ASCII card display and betting.
  """
  def __init__(self):
    """
    Initialize a new game.
    """
    self.deck = Deck()
    self.player = Player("Player", chips=200)
    self.dealer = Dealer()
    self.game_over = False

  def show_chips_info(self) -> str:
    """
    Display player's chips and current bet.
    
    Returns:
      str: Formatted chips display
    """
    output = []
    output.append("\n" + "─"*80)
    output.append(f"Your Chips: {self.player.chips} ⛀⛁ | Current Bet: {self.player.current_bet} ⛃".center(80))
    output.append("─"*80)
    return "\n".join(output)

  def get_bet(self) -> bool:
    """
    Get bet from player.
    
    Returns:
      bool: True if bet was placed successfully, False if player quit
    """
    clear_screen()
    print("\n" + "="*80)
    print("PLACE YOUR BET".center(80))
    print("="*80)
    print(f"\nAvailable Chips: {self.player.chips} ⛁".center(80))
    print("\n")
    print("Bet Options:".center(80))
    print("[1] 1 chip    [2] 5 chips    [3] 10 chips    [4] 25 chips    [5] 50 chips".center(80))
    print("\n[Q] Quit Game".center(80))
    print("="*80)
    
    valid_bets = {
      '1': 1,
      '2': 5,
      '3': 10,
      '4': 25,
      '5': 50
    }
    
    while True:
      choice = get_filtered_input("\nEnter your choice: ", "12345Q")
      
      if choice == 'Q':
        return False
      
      if choice in valid_bets:
        bet_amount = valid_bets[choice]
        if self.player.can_bet(bet_amount):
          self.player.place_bet(bet_amount)
          return True
        else:
          print(f"\n✖ Not enough chips! You have {self.player.chips} chips.")

  def setup_round(self) -> None:
    """
    Set up a new round.
    """
    # Clear hands
    self.player.clear_hand()
    self.dealer.clear_hand()

    # Create and shuffle deck
    self.deck = Deck()
    self.deck.shuffle()

    # Initial deal: 2 cards to each player
    for _ in range(2):
      self.player.receive_card(self.deck.deal_card())
      self.dealer.receive_card(self.deck.deal_card())

    self.game_over = False

  def show_initial_hands(self) -> str:
    """
    Display initial hands (dealer's first card hidden).

    Returns:
      str: Formatted display of both hands with ASCII art.
    """
    output = []
    output.append("\n" + "="*80)
    output.append("INITIAL DEAL".center(80))
    output.append("="*80)
    output.append(self.show_chips_info())
    output.append(self.dealer.show_hand_ascii(hide_first=True))
    output.append("")
    output.append(self.player.show_hand_ascii())
    output.append("="*80)
    return "\n".join(output)
  
  def show_all_hands(self) -> str:
    """
    Display all hands (nothing hidden).

    Returns:
      str: Formatted display of both hands with ASCII art.
    """
    output = []
    output.append("\n" + "="*80)
    output.append(self.show_chips_info())
    output.append(self.dealer.show_hand_ascii())
    output.append("")
    output.append(self.player.show_hand_ascii())
    output.append("="*80)
    return "\n".join(output)
  
  def player_hit(self) -> tuple[bool, str]:
    """
    Player takes a card.

    Return:
      tuple: (is_bust, message)
    """
    card = self.deck.deal_card()
    self.player.receive_card(card)

    clear_screen()
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"YOU DREW: {card}".center(80))
    output.append("="*80)
    output.append(self.show_chips_info())
    output.append(self.dealer.show_hand_ascii(hide_first=True))
    output.append("")
    output.append(self.player.show_hand_ascii())
    
    if self.player.is_bust():
      output.append("\n" + "⊘ BUST! You went over 21. ⊘".center(80))
      self.game_over = True
    
    output.append("="*80)
    message = "\n".join(output)
    
    return self.player.is_bust(), message
  
  def dealer_play(self) -> str:
    """
    Execute dealer's turn according to rules.

    Returns:
      str: Description of dealer's actions.
    """
    import time
    
    output = []
    output.append("\n" + "DEALER'S TURN".center(80))
    output.append("\nDealer reveals hidden card...")
    print("\n".join(output))
    time.sleep(1.5)
    
    clear_screen()
    
    output = []
    output.append("\n" + "DEALER'S TURN".center(80))
    output.append(self.show_chips_info())
    output.append(self.dealer.show_hand_ascii())
    output.append("")
    output.append(self.player.show_hand_ascii())
    output.append("="*80)
    print("\n".join(output))
    time.sleep(1)

    while self.dealer.should_hit():
      time.sleep(1.5)
      card = self.deck.deal_card()
      self.dealer.receive_card(card)
      
      clear_screen()
      
      output = []
      output.append("\n" + "="*80)
      output.append(f"DEALER HITS: {card}".center(80))
      output.append("="*80)
      output.append(self.show_chips_info())
      output.append(self.dealer.show_hand_ascii())
      output.append("")
      output.append(self.player.show_hand_ascii())
      
      if self.dealer.is_bust():
        output.append("\n" + "✦ DEALER BUSTS! ✦".center(80))
      
      print("\n".join(output))
      time.sleep(1)
      
      if self.dealer.is_bust():
        break

    else:
      if not self.dealer.is_bust():
        time.sleep(1)
        print("\n" + "Dealer stands.".center(80))
        time.sleep(1)

    return ""
  
  def determine_winner(self) -> str:
    """
    Determine and return the winner, updating chips accordingly.

    Returns:
      str: Winner announcement.
    """
    player_value = self.player.get_hand_value()
    dealer_value = self.dealer.get_hand_value()

    output = []
    output.append("\n" + "="*80)
    output.append("FINAL RESULT".center(80))
    output.append("="*80)
    output.append(self.dealer.show_hand_ascii())
    output.append("")
    output.append(self.player.show_hand_ascii())
    output.append("")
    output.append("-"*80)

    if self.player.is_bust():
      output.append("🃟 DEALER WINS - You busted! 🃟".center(80))
      bet_lost = self.player.current_bet
      self.player.lose_bet()
      output.append(f"You lost {bet_lost} chips 💸".center(80))
    elif self.dealer.is_bust():
      output.append("🂡 YOU WIN - Dealer busted! 🂡".center(80))
      bet_won = self.player.current_bet
      self.player.win_bet()
      output.append(f"You won {bet_won} chips! ⛃".center(80))
    elif player_value > dealer_value:
      output.append("🂱 YOU WIN - Higher hand! 🂱".center(80))
      bet_won = self.player.current_bet
      self.player.win_bet()
      output.append(f"You won {bet_won} chips! ⛃".center(80))
    elif dealer_value > player_value:
      output.append("🃟 DEALER WINS - Higher hand! 🃟".center(80))
      bet_lost = self.player.current_bet
      self.player.lose_bet()
      output.append(f"You lost {bet_lost} chips 💸".center(80))
    else:
      output.append("=+ PUSH - It's a tie! =-".center(80))
      self.player.push_bet()
      output.append("Your bet is returned.".center(80))

    output.append("-"*80)
    output.append(f"Your hand: {player_value} | Dealer's hand: {dealer_value}".center(80))
    output.append(f"Total Chips: {self.player.chips} ⛀⛁".center(80))
    output.append("="*80)
    return "\n".join(output)
  
  def play_round(self) -> bool:
    """
    Play a complete round of blackjack.
    
    Returns:
      bool: True if player wants to continue, False to quit
    """
    # Get bet first
    if not self.get_bet():
        return False
    
    clear_screen()
    self.setup_round()
    print(self.show_initial_hands())

    # Player's turn
    while not self.game_over:
        while True:
            action = get_filtered_input("\n[H]it or [S]tand? ", "HS")
            
            # Ensure only single-character input is accepted
            if len(action) > 1:
                print("✖ Pasting is not allowed. Please enter a single valid character.")
                continue
            
            break

        if action == "H":
            is_bust, message = self.player_hit()
            print(message)

            if is_bust:
                break

        elif action == "S":
            clear_screen()
            output = []
            output.append("\n" + "="*80)
            output.append("YOU CHOSE TO STAND".center(80))
            output.append("="*80)
            output.append(self.show_chips_info())
            output.append(self.dealer.show_hand_ascii(hide_first=True))
            output.append("")
            output.append(self.player.show_hand_ascii())
            output.append("="*80)
            print("\n".join(output))
            import time
            time.sleep(1)
            break

    # Dealer's turn (only if player did not bust)
    if not self.player.is_bust():
        self.dealer_play()

    # Show final result
    clear_screen()
    print(self.determine_winner())
    
    return True
