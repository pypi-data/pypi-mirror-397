"""
Input Handler module - Filtered input system for clean user interaction.
Blocks ALL paste attempts (Ctrl+V, Cmd+V, right-click, etc.)
"""

import sys
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import DummyControl
from prompt_toolkit.buffer import Buffer


def get_filtered_input(prompt: str, valid_chars: str, use_simple: bool = False) -> str:
    """
    Get input from user, only accepting specific single characters.
    Completely blocks paste attempts.
    
    Args:
        prompt: Message to display to user
        valid_chars: String containing all valid characters (e.g., "12345Q")
        use_simple: Ignored, kept for compatibility
    
    Returns:
        str: The validated input character (uppercase)
    """
    valid_chars = valid_chars.upper()
    print(prompt, end='', flush=True)
    
    kb = KeyBindings()
    result = {'value': None}
    
    # Accept only valid single characters
    for char in valid_chars:
        @kb.add(char.lower())
        @kb.add(char.upper())
        def _(event, c=char):
            print(c)  # Echo the character
            result['value'] = c
            event.app.exit()
    
    # Handle Ctrl+C and ESC to exit gracefully
    @kb.add('c-c')
    @kb.add('escape')
    def _(event):
        print()
        raise KeyboardInterrupt
    
    # Block ALL other keys including paste attempts
    @kb.add('<any>')
    def _(event):
        # Silently ignore - no feedback for invalid input
        pass
    
    # Minimal layout to avoid warnings
    layout = Layout(Window(content=DummyControl()))
    
    app = Application(
        key_bindings=kb,
        layout=layout,
        full_screen=False,
    )
    
    app.run()
    return result['value']


def wait_for_enter(prompt: str = "Press ENTER to start playing...") -> None:
    """
    Wait for the user to press ENTER only.
    Blocks all other input, including pasted content.
    """
    print(prompt, end='', flush=True)

    kb = KeyBindings()

    # Only ENTER exits
    @kb.add("enter")
    def _(event):
        print()  # Line break
        event.app.exit()

    # Ignore all other keys including paste attempts
    @kb.add("<any>")
    def _(event):
        pass  # Silently ignore

    # Minimal layout
    layout = Layout(Window(content=DummyControl()))

    app = Application(
        key_bindings=kb,
        layout=layout,
        full_screen=False,
    )

    app.run()