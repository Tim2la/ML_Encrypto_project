from pathlib import Path
from time import perf_counter

from src.cipher import reverse_key
from src.languages import LANGUAGES_BY_CHOICE, LanguageConfig
from src.ngram_model import NGramLanguageModel
from src.solver import crack_cipher
from src.text_processing import normalize_text


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIRECTORY = PROJECT_ROOT / "data"


def choose_language() -> LanguageConfig:
    print("Выберите язык шифртекста:")
    print("1 — Русский")
    print("2 — English")

    choice = input("> ").strip()

    if choice not in LANGUAGES_BY_CHOICE:
        raise ValueError("Нужно ввести 1 или 2")

    return LANGUAGES_BY_CHOICE[choice]


def load_language_model(
    language: LanguageConfig,
) -> NGramLanguageModel:
    corpus_path = DATA_DIRECTORY / language.corpus_filename

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Корпус не найден: {corpus_path}. "
            f"Запустите: python download_corpus.py --language {language.code}"
        )

    raw_corpus = corpus_path.read_text(
        encoding="utf-8",
    )
    normalized_corpus = normalize_text(
        raw_corpus,
        language.alphabet,
    )

    model = NGramLanguageModel(
        n=3,
        alpha=0.1,
        alphabet=language.alphabet + " ",
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
    alphabet: str,
) -> None:
    decryption_key = reverse_key(
        encryption_key,
    )

    print(
        "\nНайденный ключ "
        "(зашифрованная буква → обычная буква):"
    )

    for encrypted_symbol in alphabet:
        original_symbol = decryption_key[encrypted_symbol]
        print(f"{encrypted_symbol} → {original_symbol}")


def main() -> None:
    try:
        language = choose_language()

        print(
            f"\nЗагрузка и обучение модели: "
            f"{language.display_name}..."
        )
        model = load_language_model(language)
        print("Языковая модель готова.")

        ciphertext = read_ciphertext()
        normalized_ciphertext = normalize_text(
            ciphertext,
            language.alphabet,
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
            alphabet=language.alphabet,
            frequency_order=language.frequency_order,
            restarts=5,
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
            language.alphabet,
        )

    except FileNotFoundError as error:
        print(f"\nОшибка: {error}")

    except (ValueError, RuntimeError) as error:
        print(f"\nОшибка: {error}")

    except KeyboardInterrupt:
        print("\n\nРабота программы остановлена пользователем.")


if __name__ == "__main__":
    main()
