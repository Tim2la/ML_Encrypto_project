import pytest

from main import choose_language
from src.languages import ENGLISH, RUSSIAN


def test_choose_russian_language(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "1")

    assert choose_language() == RUSSIAN


def test_choose_english_language(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "2")

    assert choose_language() == ENGLISH


def test_choose_language_rejects_unknown_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "3")

    with pytest.raises(ValueError, match="1 или 2"):
        choose_language()
