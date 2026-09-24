from src.cipher import (RUSSIAN_ALPHABET, decrypt, encrypt, generate_key, is_valid_key,)

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