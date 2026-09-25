import random

from src.languages import RUSSIAN_ALPHABET

# Зашифровать
def encrypt(text: str, key: dict[str, str]) -> str:
    encrypted_symbols: list[str] = []

    for symbol in text.upper():
        if symbol in key:
            encrypted_symbols.append(key[symbol])
        else:
            encrypted_symbols.append(symbol)

    return "".join(encrypted_symbols)

# Переворот словаря
def reverse_key (key: dict[str, str]) -> dict[str,str]:
    reversed_key: dict[str, str] = {}

    for original_symbol, encrypted_symbol in key.items():
        reversed_key[encrypted_symbol] = original_symbol

    return reversed_key

# Расшифровать
def decrypt(cipher_text: str, encryption_key: dict[str, str]) -> str:
    decryption_key = reverse_key(encryption_key)
    return encrypt(cipher_text, decryption_key)

# Создание первого (рандомного) словаря
def generate_key (alphabet: str) -> dict[str, str]:
    shuffled_letters = list(alphabet)
    random.shuffle(shuffled_letters)

    key = dict(zip(alphabet, shuffled_letters))
    return key

# Проверка словаря, что все элементы, как в ключах, так и в значениях полностью покрывают алфавит
def is_valid_key(key: dict[str, str], alphabet: str) -> bool:
    original_letters = set(key.keys())
    encrypted_letters = set(key.values())
    alphabet_letters = set(alphabet)

    return (original_letters == alphabet_letters and encrypted_letters == alphabet_letters)

# Только если файл запущен напрямую, а не подключен через import 
if __name__ == "__main__":
    demo_key = generate_key(RUSSIAN_ALPHABET)
    message = "Привет мир!"

    encrypted_message = encrypt(message, demo_key)

    decrypted_message = decrypt(encrypted_message, demo_key)

    key_is_valid = is_valid_key(demo_key, RUSSIAN_ALPHABET)

    print(f"Исходный текст: {message}")
    print(f"Шифртекст: {encrypted_message}")
    print(f"Расшифрованный текст: {decrypted_message}")
    print(f"Ключ корректный: {key_is_valid}")
