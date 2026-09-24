from src.cipher import (RUSSIAN_ALPHABET, decrypt, encrypt, generate_key, is_valid_key,)
from src.text_processing import (normalize_text)

def test_encrypt_replaces_known_letters() -> None:
    key = {
        "А": "Х",
        "Б": "П",
    }

    result = encrypt("АББА!", key)

    assert result == "ХППХ!"

def test_encrypt_then_decrypt_returns_original_text() -> None:
    key = generate_key(RUSSIAN_ALPHABET)
    original_text = "ПРИВЕТ, МИР!"

    encrypted_text = encrypt(original_text, key)
    decrypted_text = decrypt(encrypted_text, key)

    assert decrypted_text == original_text


def test_generated_key_is_valid() -> None:
    key = generate_key(RUSSIAN_ALPHABET)

    assert is_valid_key(key, RUSSIAN_ALPHABET) is True

def test_normilaze_text_removex_exstra_symbols() -> None:
    text = "Привет       мир! 123"
    true_text = "ПРИВЕТ МИР"
    
    assert true_text == normalize_text(text)