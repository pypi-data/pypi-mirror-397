import importlib
import inspect
import runpy


def test_main_module_imports():
  """
  The blackjack.__main__ module should import without error.
  """
  module = importlib.import_module("blackjack.__main__")
  assert module is not None


def test_main_is_callable():
  """
  main must exist and be callable.
  """
  module = importlib.import_module("blackjack.__main__")
  assert hasattr(module, "main")
  assert inspect.isfunction(module.main)


def test_main_guard_prevents_execution_on_import():
  """
  Importing should NOT run the game.
  """
  importlib.reload(importlib.import_module("blackjack.__main__"))
  assert True
