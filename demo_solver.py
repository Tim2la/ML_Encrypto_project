import random

from pathlib import Path

from src.cipher import (RUSSIAN_ALPHABET, decrypt, encrypt, generate_key)
from src.ngram_model import NGramLanguageModel
from src.solver import (generate_frequency_key, solve_with_restarts)
from src.text_processing import normalize_text


CORPUS_PATH = Path("data/wikipedia_ru.txt")


def calculate_accuracy(
    original_text: str,
    decrypted_text: str,
) -> float:
    original_letters = normalize_text(original_text).replace(" ", "")
    decrypted_letters = normalize_text(decrypted_text).replace(" ", "")

    correct_letters = sum(
        original == decrypted
        for original, decrypted in zip(
            original_letters,
            decrypted_letters,
        )
    )

    return correct_letters / len(original_letters)


def main() -> None:
    print("Загрузка корпуса...")

    corpus = CORPUS_PATH.read_text(encoding="utf-8")
    normalized_corpus = normalize_text(corpus)

    print("Обучение языковой модели...")

    model = NGramLanguageModel(n=3, alpha=0.1)
    model.fit(normalized_corpus)

    plaintext = (
        "КРИПТОГРАФИЯ ПОМОГАЕТ ЗАЩИЩАТЬ ИНФОРМАЦИЮ "
        "ОТ НЕСАНКЦИОНИРОВАННОГО ДОСТУПА. "
        "В ЭТОМ ПРОЕКТЕ МЫ СОЗДАЕМ ПРОГРАММУ, "
        "КОТОРАЯ ИСПОЛЬЗУЕТ ЯЗЫКОВУЮ МОДЕЛЬ "
        "И МЕТОД ИМИТАЦИИ ОТЖИГА ДЛЯ ВЗЛОМА "
        "ШИФРА ПРОСТОЙ ЗАМЕНЫ. "
        "АЛГОРИТМ ПЕРЕБИРАЕТ РАЗНЫЕ КЛЮЧИ "
        "И ВЫБИРАЕТ ВАРИАНТ, КОТОРЫЙ БОЛЬШЕ "
        "ВСЕГО ПОХОЖ НА НОРМАЛЬНЫЙ РУССКИЙ ТЕКСТ."
    )
    random.seed(42)

    real_key = generate_key(RUSSIAN_ALPHABET)

    ciphertext = encrypt(plaintext, real_key)

    initial_key = generate_frequency_key(ciphertext)

    print("Запуск расшифровки...")

    best_key, best_score = solve_with_restarts(
        ciphertext=ciphertext,
        initial_key=initial_key,
        model=model,
        restarts=3,
        iterations_per_restart=20_000,
        start_temperature=0.03,
        cooling_rate=0.9995,
        seed=42,
    )

    decrypted_text = decrypt(ciphertext, best_key)

    accuracy = calculate_accuracy(plaintext, decrypted_text)

    print("\nИсходный текст:")
    print(plaintext)

    print("\nШифртекст:")
    print(ciphertext)

    print("\nРезультат расшифровки:")
    print(decrypted_text)

    print(f"\nОценка модели: {best_score:.4f}")
    print(f"Точность расшифровки: {accuracy:.2%}")


if __name__ == "__main__":
    main()