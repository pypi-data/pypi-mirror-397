"""
Demo script to visualize ASCII card representations.
"""

from blackjack.card import Card

def demo_cards():
  """
  Demonstrate ASCII card art for different cards.
  """
  print("\n" + "="*80)
  print("BLACKJACK - ASCII CARD ART DEMO".center(80))
  print("="*80 + "\n")
  
  # Demo individual cards
  print("Individual Cards:")
  print("-" * 80)
  
  demo_ranks = [('A', '♠'), ('K', '♥'), ('Q', '♦'), ('J', '♣'), ('10', '♠'), ('2', '♥')]
  
  for rank, suit in demo_ranks:
    card = Card(rank, suit)
    print(f"\n{card}")
    for line in card.get_ascii_art():
      print(line)
  
  # Demo hidden card
  print("\n\nHidden Card (back of card):")
  print("-" * 80)
  for line in Card.get_hidden_card_ascii():
    print(line)
  
  # Demo multiple cards side by side
  print("\n\nMultiple Cards Side by Side:")
  print("-" * 80)
  
  cards = [
    Card('A', '♠'),
    Card('K', '♥'),
    Card('Q', '♦')
  ]
  
  # Get all card ASCII arts
  cards_ascii = [card.get_ascii_art() for card in cards]
  
  # Print them side by side
  for line_index in range(7):
    line_parts = [card_lines[line_index] for card_lines in cards_ascii]
    print("  ".join(line_parts))
  
  print("\n" + "="*80 + "\n")

if __name__ == "__main__":
  demo_cards()