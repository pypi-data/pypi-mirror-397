"""
Deck module - Manages a deck of 52 playing cards.
"""

import random
from typing import List
from .card import Card

class Deck:
  """
  Represents a standard 52-card deck.

  Design Choice: Encapsulates all deck operations (creation, shuffling, dealing).
  Uses composition - creates Card objects rather than simples values.
  """
  def __init__(self):
    """
    Initialize a new deck with 52 cards.
    """
    self.cards: List[Card] = []
    self._create_deck()

  def _create_deck(self):
    """
    Create a standard 52-card deck.
    """
    self.cards = [
      Card(rank, suit)
      for suit in Card.SUITS
      for rank in Card.RANKS
    ]

  def shuffle(self):
    """
    Shuffle the deck randomly.

    Design Choice: Uses random.shuffle for true randomness.
    """
    random.shuffle(self.cards)

  def deal_card(self) -> Card:
    """
    Deal (remove and return) the top card from the deck.
    
    Returns:
      Card: The dealt card.

    Raises:
      IndexError: If deck is empty.
    """
    if not self.cards:
      raise IndexError("Cannot deal from empty deck.")
    return self.cards.pop()
  
  def cards_remaining(self) -> int:
    """
    Get the number of cards remaining in the deck.
    """
    return len(self.cards)
  
  def __len__(self) -> int:
    """
    Return number of cards in the deck.
    """
    return len(self.cards)
  
  def __str__(self) -> str:
    """
    String representation of the deck.
    """
    return f"Deck with {len(self.cards)} cards"