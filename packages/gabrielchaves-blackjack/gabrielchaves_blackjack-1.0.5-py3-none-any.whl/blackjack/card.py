"""
Card module - Represents a single playing card with ASCII art.
"""

class Card:
  """
  Represents a single playing card with ASCII art representation.
  """

  RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
  SUITS = ['♠', '♥', '♦', '♣']

  def __init__(self, rank: str, suit: str):
    """
    Initialize a card with rank and suit.

    Args:
      rank: Card rank (2-10, J, Q, K, A)
      suit: Card suit (♠, ♥, ♦, ♣)
    """
    if rank not in self.RANKS:
      raise ValueError(f"Invalid rank: {rank}")
    if suit not in self.SUITS:
      raise ValueError(f"Invalid suit: {suit}")
    
    self.rank = rank
    self.suit = suit

  @property
  def value(self) -> int:
    """
    Get the numeric value of the card.

    Returns:
      int: Card value (2-11)
    """
    if self.rank in ['J', 'Q', 'K']:
      return 10
    elif self.rank == 'A':
      return 11
    else:
      return int(self.rank)
  
  def get_ascii_art(self) -> list:
    """
    Get ASCII art representation of the card.
    
    Returns:
      list: List of strings representing each line of the card
    """
    # Determine the spacing for rank.
    rank_display = self.rank.ljust(2) if len(self.rank) == 1 else self.rank
    
    lines = [
      "┌─────────┐",
      f"│{rank_display}       │",
      "│         │",
      f"│    {self.suit}    │",
      "│         │",
      f"│       {rank_display}│",
      "└─────────┘"
    ]
    return lines
  
  @staticmethod
  def get_hidden_card_ascii() -> list:
    """
    Get ASCII art for a hidden card (back of card).
    
    Returns:
      list: List of strings representing a hidden card
    """
    lines = [
      "┌─────────┐",
      "│░░░░░░░░░│",
      "│░░░░░░░░░│",
      "│░░░░░░░░░│",
      "│░░░░░░░░░│",
      "│░░░░░░░░░│",
      "└─────────┘"
    ]
    return lines
    
  def __str__(self) -> str:
    """
    String representation of the card.
    """
    return f"{self.rank}{self.suit}"
  
  def __repr__(self) -> str:
    """
    Developer representation of the card.
    """
    return f"Card(rank='{self.rank}', suit='{self.suit}')"