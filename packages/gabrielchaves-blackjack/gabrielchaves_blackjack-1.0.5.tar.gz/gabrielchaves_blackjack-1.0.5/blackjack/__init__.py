"""
A BlackJack Game Package

A text-based implementation of BlackJack (21) game.
"""

__version__ = "1.0.5"
__author__ = "Gabriel Chaves"

from .game import BlackJackGame
from .cli import main

__all__ = ["BlackJackGame", "main"]