"""
Hand module - Represents a hand of cards.
"""

from typing import List
from .card import Card

class Hand:
  """
  Represents a hand of cards.
  
  Design Choice: Separates hand management from player logic.
  Handles value calculation and card storage.
  """
  def __init__(self):
    """
    Initialize an empty hand.
    """
    self.cards: List[Card] = []

  def add_card(self, card: Card):
    """
    Add a card to the hand.
    
    Args:
      card: Card to add
    """
    self.cards.append(card)

  def get_value(self) -> int:
    """
    Calculate the total value of the hand.

    Returns:
      int: Total value of all cards in hand.
    
    Design Choice: Simple sum as per basic requirements.
    Aces are always 11 in this version.
    """
    return sum(card.value for card in self.cards)
  
  def is_bust(self) -> bool:
    """
    Check if hand value exceeds 21.
    
    Returns:
      bool: True if hand is bust (over 21)
    """
    return self.get_value() > 21
  
  def is_blackjack(self) -> bool:
    """
    Check if hand is a natural blackjack (21 with 2 cards).
    
    Returns:
      bool: True if hand is blackjack
    """
    return len(self.cards) == 2 and self.get_value() == 21
  
  def clear(self) -> None:
    """
    Clear all cards from the hand.
    """
    self.cards.clear()

  def __str__(self) -> str:
    """
    String representation of hand.
    """
    cards_str = ', '.join(str(card) for card in self.cards)
    return f"[{cards_str}] (Value: {self.get_value()})"
  
  def __len__(self) -> int:
    """
    Return number of cards in hand.
    """
    return len(self.cards)