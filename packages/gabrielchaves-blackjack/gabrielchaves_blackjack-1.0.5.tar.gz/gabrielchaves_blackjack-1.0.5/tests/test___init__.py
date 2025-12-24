import importlib
import inspect

import blackjack


def test_package_imports_without_error():
  """
  The package should import without throwing exceptions.
  """
  assert blackjack is not None


def test_metadata_version():
  """
  Check if the version is set correctly.
  """
  assert hasattr(blackjack, "__version__")
  assert isinstance(blackjack.__version__, str)
  assert blackjack.__version__ == "1.0.5"


def test_metadata_author():
  """
  Check if the author is set correctly.
  """
  assert hasattr(blackjack, "__author__")
  assert isinstance(blackjack.__author__, str)
  assert blackjack.__author__ == "Gabriel Chaves"


def test_blackjackgame_is_exposed():
  """
  BlackJackGame should be available in the package namespace.
  """
  assert hasattr(blackjack, "BlackJackGame")


def test_blackjackgame_is_class():
  """
  BlackjackGame should be a real class.
  """
  assert inspect.isclass(blackjack.BlackJackGame)


def test_main_is_exposed():
  """
  main must be available in the package's namespace.
  """
  assert hasattr(blackjack, "main")


def test_main_is_callable():
  """
  The main function must be callable.
  """
  assert callable(blackjack.main)


def test_all_is_defined():
  """
  __all__ must exist and be a list or tuple.
  """
  assert hasattr(blackjack, "__all__")
  assert isinstance(blackjack.__all__, (list, tuple))


def test_all_contains_expected_exports():
  """
  __all__ should contain only the expected public symbols.
  """
  assert "BlackJackGame" in blackjack.__all__
  assert "main" in blackjack.__all__


def test_all_exports_are_accessible():
  """
  Everything in __all__ should be accessible via the package.
  """
  for name in blackjack.__all__:
      assert hasattr(blackjack, name)


def test_direct_import_matches_internal_import():
  """
  The object imported via __init__ must be the same as the object in the original module.
  """
  game_module = importlib.import_module("blackjack.game")
  cli_module = importlib.import_module("blackjack.cli")

  assert blackjack.BlackJackGame is game_module.BlackJackGame
  assert blackjack.main is cli_module.main


def test_reimport_package_is_idempotent():
  """
  Reimporting the package should not alter the exposed objects.
  """
  first_game_class = blackjack.BlackJackGame
  first_main_func = blackjack.main

  reloaded = importlib.reload(blackjack)

  assert reloaded.BlackJackGame is first_game_class
  assert reloaded.main is first_main_func
