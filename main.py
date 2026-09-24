from pathlib import Path
from time import perf_counter

from src.cipher import RUSSIAN_ALPHABET, reverse_key
from src.ngram_model import NGramLanguageModel
from src.solver import crack_cipher
from src.text_processing import normalize_text


PROJECT_ROOT = Path(__file__).resolve().parent
CORPUS_PATH = PROJECT_ROOT / "data" / "wikipedia_ru.txt"


def load_language_model() -> NGramLanguageModel:
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(
            f"Корпус не найден: {CORPUS_PATH}"
        )

    raw_corpus = CORPUS_PATH.read_text(
        encoding="utf-8",
    )
    normalized_corpus = normalize_text(raw_corpus)

    model = NGramLanguageModel(
        n=3,
        alpha=0.1,
    )
    model.fit(normalized_corpus)

    return model


def read_ciphertext() -> str:
    print(
        "\nВставьте шифртекст."
        "\nПосле последней строки нажмите Enter ещё раз:"
    )

    lines: list[str] = []

    while True:
        try:
            line = input()
        except EOFError:
            break

        if line == "":
            break

        lines.append(line)

    return "\n".join(lines)


def print_decryption_key(
    encryption_key: dict[str, str],
) -> None:
    decryption_key = reverse_key(
        encryption_key,
    )

    print(
        "\nНайденный ключ "
        "(зашифрованная буква → обычная буква):"
    )

    for encrypted_symbol in RUSSIAN_ALPHABET:
        original_symbol = decryption_key[encrypted_symbol]

        print(
            f"{encrypted_symbol} → {original_symbol}"
        )


def main() -> None:
    try:
        print("Загрузка и обучение языковой модели...")

        model = load_language_model()

        print("Языковая модель готова.")

        ciphertext = read_ciphertext()

        normalized_ciphertext = normalize_text(
            ciphertext,
        )
        letters_count = len(
            normalized_ciphertext.replace(" ", "")
        )

        if letters_count < 100:
            print(
                "\nПредупреждение: шифртекст короткий. "
                "Качество расшифровки может быть низким."
            )

        print("\nРасшифрование началось...")

        start_time = perf_counter()

        decrypted_text, best_key, best_score = crack_cipher(
            ciphertext=ciphertext,
            model=model,
            restarts=3,
            iterations_per_restart=20_000,
            start_temperature=0.03,
            cooling_rate=0.9995,
            seed=42,
        )

        elapsed_time = perf_counter() - start_time

        print("\nИсходный шифртекст:")
        print(ciphertext)

        print("\nРезультат расшифровки:")
        print(decrypted_text)

        print(f"\nОценка модели: {best_score:.4f}")
        print(f"Время работы: {elapsed_time:.2f} секунд")

        print_decryption_key(
            best_key,
        )

    except FileNotFoundError as error:
        print(f"\nОшибка: {error}")

    except (ValueError, RuntimeError) as error:
        print(f"\nОшибка: {error}")

    except KeyboardInterrupt:
        print("\n\nРабота программы остановлена пользователем.")


if __name__ == "__main__":
    main()