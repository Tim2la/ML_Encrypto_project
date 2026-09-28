from src.languages import ENGLISH_ALPHABET, RUSSIAN_ALPHABET
from src.text_processing import compact_ciphertext, normalize_text

def test_normilaze_text_removex_exstra_symbols() -> None:
    text = "Привет       мир! 123"
    true_text = "ПРИВЕТ МИР"
    
    assert true_text == normalize_text(text)


def test_normalize_english_text() -> None:
    text = "Hello,   world! 123"

    assert normalize_text(text, ENGLISH_ALPHABET) == "HELLO WORLD"


def test_compact_russian_ciphertext_removes_block_boundaries() -> None:
    assert compact_ciphertext("аб вг\nд!?", RUSSIAN_ALPHABET) == "АБВГД"


def test_compact_english_ciphertext_removes_block_boundaries() -> None:
    assert compact_ciphertext("ab cd\nef!?", ENGLISH_ALPHABET) == "ABCDEF"
