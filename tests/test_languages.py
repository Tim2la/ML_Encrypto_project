from src.languages import (
    ENGLISH,
    ENGLISH_ALPHABET,
    ENGLISH_FREQUENCY_ORDER,
    LANGUAGES_BY_CHOICE,
    RUSSIAN,
    RUSSIAN_ALPHABET,
    RUSSIAN_FREQUENCY_ORDER,
)


def test_frequency_orders_match_alphabets() -> None:
    assert set(RUSSIAN_FREQUENCY_ORDER) == set(RUSSIAN_ALPHABET)
    assert set(ENGLISH_FREQUENCY_ORDER) == set(ENGLISH_ALPHABET)


def test_language_choices_are_configured() -> None:
    assert LANGUAGES_BY_CHOICE["1"] == RUSSIAN
    assert LANGUAGES_BY_CHOICE["2"] == ENGLISH
    assert RUSSIAN.corpus_filename == "wikipedia_ru.txt"
    assert ENGLISH.corpus_filename == "wikipedia_en.txt"
