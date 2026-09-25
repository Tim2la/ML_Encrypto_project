from src.languages import RUSSIAN_ALPHABET

# Нормализируем текст, поднимаем в верхний регист и убираем символы не из алфавита
def normalize_text(text:str, alphabet:str = RUSSIAN_ALPHABET) -> str:
    normalized_symbols: list[str] = []

    for symbol in text.upper():
        if symbol in alphabet:
            normalized_symbols.append(symbol)
        else:
            normalized_symbols.append(" ")

    normalized_text = "".join(normalized_symbols)
    return " ".join(normalized_text.split())
