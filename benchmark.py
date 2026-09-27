import random
from pathlib import Path
from statistics import mean
from time import perf_counter

from main import load_language_model
from src.cipher import encrypt
from src.evaluation import letter_accuracy
from src.languages import ENGLISH, RUSSIAN, LanguageConfig
from src.solver import crack_cipher


PROJECT_ROOT = Path(__file__).resolve().parent


def take_first_letters(
    text: str,
    alphabet: str,
    limit: int,
) -> str:
    if limit <= 0:
        raise ValueError("Количество букв должно быть положительным")

    letters_seen = 0

    for index, symbol in enumerate(text):
        if symbol.upper() in alphabet:
            letters_seen += 1

            if letters_seen == limit:
                return text[:index + 1]

    raise ValueError("В тексте меньше букв, чем запрошено")


def evaluate_language(
    language: LanguageConfig,
    text_number: int,
    limit: int,
) -> tuple[float, float]:
    text_path = (
        PROJECT_ROOT
        / "data"
        / f"evaluation_{language.code}_{text_number}.txt"
    )
    full_text = text_path.read_text(encoding="utf-8").strip()
    original_text = take_first_letters(
        full_text,
        language.alphabet,
        limit,
    )

    seed = 40 + text_number
    random_generator = random.Random(seed)

    shuffled_letters = list(language.alphabet)
    random_generator.shuffle(shuffled_letters)
    encryption_key = dict(zip(language.alphabet, shuffled_letters))

    ciphertext = encrypt(original_text, encryption_key)
    model = load_language_model(language)

    start_time = perf_counter()
    decrypted_text, _, score = crack_cipher(
        ciphertext=ciphertext,
        model=model,
        alphabet=language.alphabet,
        frequency_order=language.frequency_order,
        restarts=5,
        iterations_per_restart=20_000,
        start_temperature=0.03,
        cooling_rate=0.9995,
        seed=seed,
    )
    elapsed_seconds = perf_counter() - start_time

    accuracy = letter_accuracy(
        original_text,
        decrypted_text,
        language.alphabet,
    )

    print(f"\nЯзык: {language.display_name}")
    print(f"Текст № {text_number}")
    print(f"Длина: {limit} букв")
    print(f"Точность: {accuracy:.2%}")
    print(f"Время: {elapsed_seconds:.2f} с")
    print(f"Оценка модели: {score:.4f}")

    return accuracy, elapsed_seconds


def main() -> None:
    for language in (RUSSIAN, ENGLISH):
        for limit in (100, 200, 350):
            results = [
                evaluate_language(language, text_number, limit)
                for text_number in (1, 2, 3)
            ]

            accuracies = [accuracy for accuracy, _ in results]
            times = [seconds for _, seconds in results]
            fully_correct = sum(
                accuracy == 1.0 for accuracy in accuracies
            )

            print(
                f"\nИтог: {language.display_name}, "
                f"{limit} букв"
            )
            print(f"Средняя точность: {mean(accuracies):.2%}")
            print(
                f"Полностью верно: "
                f"{fully_correct} из {len(results)}"
            )
            print(f"Среднее время: {mean(times):.2f} с")


if __name__ == "__main__":
    main()
    