from collections import Counter
from pathlib import Path
from time import perf_counter

from src.cipher import reverse_key
from src.languages import LANGUAGES_BY_CHOICE, LanguageConfig
from src.model_storage import load_model
from src.ngram_model import NGramLanguageModel
from src.solver import crack_cipher
from src.text_processing import compact_ciphertext, normalize_text
from src.word_segmentation import count_words, segment_text


PROJECT_ROOT = Path(__file__).resolve().parent
MODELS_DIRECTORY = PROJECT_ROOT / "models"
DATA_DIRECTORY = PROJECT_ROOT / "data"


def choose_language() -> LanguageConfig:
    print("Выберите язык шифртекста:")
    print("1 — Русский")
    print("2 — English")

    choice = input("> ").strip()

    if choice not in LANGUAGES_BY_CHOICE:
        raise ValueError("Нужно ввести 1 или 2")

    return LANGUAGES_BY_CHOICE[choice]


def choose_ciphertext_format() -> bool:
    print("\nКак расположены пробелы в шифртексте?")
    print("1 — между словами")
    print("2 — между искусственными блоками букв")

    choice = input("> ").strip()
    if choice not in ("1", "2"):
        raise ValueError("Нужно ввести 1 или 2")

    return choice == "2"


def load_language_model(
    language: LanguageConfig,
    n: int = 3,
    compact: bool = False,
) -> NGramLanguageModel:
    # Обычная и «без пробелов» модели обучены на разных видах текста.
    if compact:
        if n != 3:
            raise ValueError("Для текста без пробелов доступна только 3-граммная модель")
        model_path = MODELS_DIRECTORY / f"{language.code}_model_3_compact.pkl"
    else:
        model_path = MODELS_DIRECTORY / f"{language.code}_model_{n}_gramm.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}. "
            "Сначала запустите: python train_models.py"
        )

    return load_model(model_path)


def load_word_counts(language: LanguageConfig) -> Counter[str] | None:
    corpus_path = DATA_DIRECTORY / language.corpus_filename
    if not corpus_path.exists():
        return None

    # Частоты слов нужны только для приблизительного восстановления пробелов.
    corpus = corpus_path.read_text(encoding="utf-8")
    return count_words(normalize_text(corpus, language.alphabet))


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
        compact = choose_ciphertext_format()

        print(
            f"\nЗагрузка: "
            f"{language.display_name}..."
        )
        model = load_language_model(language, compact=compact)
        print("Языковая модель готова.")

        ciphertext = read_ciphertext()
        # Удаляем границы блоков до поиска ключа, но оставляем исходный ввод для вывода.
        ciphertext_for_solver = (
            compact_ciphertext(ciphertext, language.alphabet)
            if compact
            else ciphertext
        )
        normalized_ciphertext = normalize_text(
            ciphertext_for_solver,
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
            ciphertext=ciphertext_for_solver,
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

        if compact:
            word_counts = load_word_counts(language)
            if word_counts:
                print("\nПредположительная разбивка на слова (буквы не исправлены):")
                print(segment_text(decrypted_text, word_counts))
            else:
                print("\nКорпус не найден: приблизительная разбивка на слова недоступна.")
            print("Границы слов определены приблизительно, отдельные буквы могут быть неверны.")

        print(f"\nОценка модели: {best_score:.4f}")
        print(f"Время поиска: {elapsed_time:.2f} секунд")

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
