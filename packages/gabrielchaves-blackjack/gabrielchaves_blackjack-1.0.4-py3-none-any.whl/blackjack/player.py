"""
Player module - Represents player in the game with ASCII card display and chips.
"""
from .hand import Hand
from .card import Card

class Player:
    """
    Represents a player in the game.
    """

    def __init__(self, name: str, chips: int = 200):
        self.name = name
        self.hand = Hand()
        self.chips = chips
        self.current_bet = 0

    def place_bet(self, amount: int) -> bool:
        if amount <= 0 or amount > self.chips:
            return False
        self.current_bet = amount
        return True

    def win_bet(self) -> None:
        self.chips += self.current_bet
        self.current_bet = 0

    def lose_bet(self) -> None:
        self.chips -= self.current_bet
        self.current_bet = 0

    def push_bet(self) -> None:
        self.current_bet = 0

    def has_chips(self) -> bool:
        return self.chips > 0

    def can_bet(self, amount: int) -> bool:
        return amount <= self.chips

    def receive_card(self, card) -> None:
        self.hand.add_card(card)

    def show_hand_ascii(self, hide_first: bool = False) -> str:
        if len(self.hand.cards) == 0:
            return f"{self.name}: No cards"

        cards_ascii = []
        for i, card in enumerate(self.hand.cards):
            if hide_first and i == 0:
                cards_ascii.append(Card.get_hidden_card_ascii())
            else:
                cards_ascii.append(card.get_ascii_art())

        combined_lines = []
        for line_index in range(7):
            line_parts = []
            for card_lines in cards_ascii:
                line_parts.append(card_lines[line_index])
            combined_lines.append("  ".join(line_parts))

        if hide_first and len(self.hand.cards) > 0:
            visible_value = sum(card.value for card in self.hand.cards[1:])
            value_text = f"Visible Value: {visible_value}"
        else:
            value_text = f"Value: {self.hand.get_value()}"

        result = f"\n{self.name}'s Hand - {value_text}\n"
        result += "\n".join(combined_lines)
        return result

    def show_hand(self, hide_first: bool = False) -> str:
        if hide_first and len(self.hand.cards) > 0:
            visible_cards = self.hand.cards[1:]
            cards_str = '[Hidden], ' + ', '.join(str(card) for card in visible_cards)
            visible_value = sum(card.value for card in visible_cards)
            return f"{self.name}: {cards_str} (Visible: {visible_value})"
        else:
            return f"{self.name}: {self.hand}"

    def get_hand_value(self) -> int:
        return self.hand.get_value()

    def is_bust(self) -> bool:
        return self.hand.is_bust()

    def clear_hand(self) -> None:
        self.hand.clear()

class Dealer(Player):
    """
    Represents the dealer with strict strategy.
    """
    def __init__(self):
        super().__init__("Dealer", chips=0)

    def should_hit(self) -> bool:
        """
        Dealer strategy based on two-card hand and table strategy.
        Soft hands are considered (Ace counted as 11).
        """
        cards = self.hand.cards
        if len(cards) != 2:
            # Always apply strategy strictly, even if more than 2 cards
            value = self.hand.get_value()
            aces = sum(1 for c in cards if c.rank == 'A')
            soft_value = value
            while soft_value > 21 and aces > 0:
                soft_value -= 10
                aces -= 1
            value = soft_value

            # If value >= 17, stand
            if value >= 17:
                return False
            return True

        # Two-card strategy
        value = self.hand.get_value()
        ranks = [c.rank for c in cards]
        dealer_up = cards[1].value  # Second card is dealer's up card for strategy

        # Detect soft hand
        is_soft = 'A' in ranks
        other_card = next(c.value for c in cards if c.rank != 'A') if is_soft else None

        if is_soft:
            # Soft hands (A+2 to A+9)
            if other_card in [8, 9]:  # A+8; A+9
                return False
            elif other_card == 7:  # A+7
                return dealer_up in [7,8,9,10,11] and True or False
            elif other_card in [2,3,4,5,6]:  # A+2 to A+6
                return True
            else:  # A+10? treat as 21
                return False
        else:
            # Hard hands
            if value >= 17:
                return False
            elif 13 <= value <= 16:
                return dealer_up in [2,3,4,5,6] and False or True
            elif value == 12:
                return dealer_up in [4,5,6] and False or True
            else:  # 4-11
                return True
