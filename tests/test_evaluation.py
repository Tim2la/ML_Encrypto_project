import pytest

from src.evaluation import letter_accuracy
from src.languages import ENGLISH_ALPHABET, RUSSIAN_ALPHABET


def test_letter_accuracy_counts_only_letters() -> None:
    result = letter_accuracy(
        original="Hello!",
        predicted="HEXXO?",
        alphabet=ENGLISH_ALPHABET,
    )

    assert result == 0.6


def test_letter_accuracy_for_identical_text() -> None:
    result = letter_accuracy(
        original="ПРИВЕТ, МИР!",
        predicted="ПРИВЕТ, МИР!",
        alphabet=RUSSIAN_ALPHABET,
    )

    assert result == 1.0


def test_letter_accuracy_rejects_different_lengths() -> None:
    with pytest.raises(ValueError, match="Длины текстов"):
        letter_accuracy("HELLO", "HELL", ENGLISH_ALPHABET)


def test_letter_accuracy_rejects_text_without_letters() -> None:
    with pytest.raises(ValueError, match="нет букв"):
        letter_accuracy("!!!", "???", ENGLISH_ALPHABET)