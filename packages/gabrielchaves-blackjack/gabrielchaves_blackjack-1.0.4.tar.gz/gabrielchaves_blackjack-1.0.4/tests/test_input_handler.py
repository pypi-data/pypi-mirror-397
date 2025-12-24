import pytest
from unittest.mock import patch

from blackjack.input_handler import get_filtered_input, wait_for_enter


# ======================================================
# Fake Application (sem console, sem Win32)
# ======================================================

class FakeApp:
    def __init__(self, key_bindings=None, **kwargs):
        self.key_bindings = key_bindings
        self.exited = False

    def run(self):
        # Não faz nada automaticamente
        pass

    def exit(self):
        self.exited = True


class DummyEvent:
    def __init__(self, app):
        self.app = app


# ======================================================
# Helpers
# ======================================================

def press_key(app, key):
    """
    Dispara o handler correspondente à tecla,
    considerando aliases reais do prompt_toolkit.
    """
    aliases = {
        "enter": {"enter", "c-m", "\r", "\n"},
        "<any>": {"<any>"},
        "c-c": {"c-c"},
        "escape": {"escape"},
    }

    expected = aliases.get(key, {key})

    for binding in app.key_bindings.bindings:
        if any(k in expected for k in binding.keys):
            binding.handler(DummyEvent(app))
            return

    raise AssertionError(f"Key {key} not bound (available: {[b.keys for b in app.key_bindings.bindings]})")



# ======================================================
# get_filtered_input
# ======================================================

def test_get_filtered_input_accepts_valid_char():
    def fake_application(*args, **kwargs):
        return FakeApp(*args, **kwargs)

    with patch("blackjack.input_handler.Application", fake_application):
        app_holder = {}

        def fake_run(self):
            app_holder["app"] = self
            press_key(self, "1")

        FakeApp.run = fake_run

        result = get_filtered_input("Enter choice: ", "123Q")

    assert result == "1"


def test_get_filtered_input_accepts_lowercase():
    with patch("blackjack.input_handler.Application", FakeApp):
        def fake_run(self):
            press_key(self, "q")

        FakeApp.run = fake_run
        result = get_filtered_input("Enter choice: ", "123Q")

    assert result == "Q"


def test_get_filtered_input_blocks_invalid_key():
    with patch("blackjack.input_handler.Application", FakeApp):
        def fake_run(self):
            press_key(self, "<any>")
            self.exit()

        FakeApp.run = fake_run
        result = get_filtered_input("Enter choice: ", "123Q")

    assert result is None


def test_get_filtered_input_ctrl_c_raises():
    with patch("blackjack.input_handler.Application", FakeApp):
        def fake_run(self):
            press_key(self, "c-c")

        FakeApp.run = fake_run
        with pytest.raises(KeyboardInterrupt):
            get_filtered_input("Enter choice: ", "123Q")


def test_get_filtered_input_escape_raises():
    with patch("blackjack.input_handler.Application", FakeApp):
        def fake_run(self):
            press_key(self, "escape")

        FakeApp.run = fake_run
        with pytest.raises(KeyboardInterrupt):
            get_filtered_input("Enter choice: ", "123Q")


# ======================================================
# wait_for_enter
# ======================================================

def test_wait_for_enter_accepts_enter():
    with patch("blackjack.input_handler.Application", FakeApp):
        def fake_run(self):
            press_key(self, "enter")

        FakeApp.run = fake_run
        wait_for_enter("Press ENTER")


def test_wait_for_enter_blocks_other_keys():
    with patch("blackjack.input_handler.Application", FakeApp):
        def fake_run(self):
            press_key(self, "<any>")
            self.exit()

        FakeApp.run = fake_run
        wait_for_enter("Press ENTER")
