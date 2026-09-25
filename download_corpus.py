import argparse
import gc
import os
from pathlib import Path
import sys

from datasets import load_dataset

from src.languages import LANGUAGES_BY_CODE, LanguageConfig


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIRECTORY = PROJECT_ROOT / "data"
TARGET_CHARACTERS = 10_000_000


def download_corpus(
    language: LanguageConfig,
    target_characters: int,
    output_directory: Path = DATA_DIRECTORY,
) -> Path:
    output_path = output_directory / language.corpus_filename

    print(
        f"Загрузка корпуса: {language.display_name} "
        f"({target_characters:,} символов)..."
    )

    dataset = load_dataset(
        "wikimedia/wikipedia",
        language.wikipedia_config,
        split="train",
        streaming=True,
    )

    articles: list[str] = []
    total_characters = 0

    article_iterator = iter(dataset)

    try:
        while total_characters < target_characters:
            article = next(article_iterator)
            text = article["text"].strip()

            if not text:
                continue

            articles.append(text)
            total_characters += len(text)
    except StopIteration:
        pass
    finally:
        close_iterator = getattr(article_iterator, "close", None)

        if close_iterator is not None:
            close_iterator()

    del article_iterator
    del dataset
    gc.collect()

    corpus = "\n".join(articles)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        corpus,
        encoding="utf-8",
    )

    print(f"Собрано статей: {len(articles)}")
    print(f"Собрано символов: {len(corpus)}")
    print(f"Корпус сохранён: {output_path}")

    return output_path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Скачивание корпусов Википедии для языковой модели",
    )
    parser.add_argument(
        "--language",
        choices=("ru", "en", "all"),
        default="ru",
        help="язык корпуса: ru, en или all (по умолчанию ru)",
    )
    parser.add_argument(
        "--target-characters",
        type=int,
        default=TARGET_CHARACTERS,
        help="целевое количество символов",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DATA_DIRECTORY,
        help=argparse.SUPPRESS,
    )

    arguments = parser.parse_args()

    if arguments.target_characters <= 0:
        parser.error("--target-characters должно быть положительным числом")

    return arguments


def main() -> None:
    arguments = parse_arguments()

    if arguments.language == "all":
        selected_languages = list(LANGUAGES_BY_CODE.values())
    else:
        selected_languages = [
            LANGUAGES_BY_CODE[arguments.language]
        ]

    for language in selected_languages:
        download_corpus(
            language=language,
            target_characters=arguments.target_characters,
            output_directory=arguments.output_directory,
        )


if __name__ == "__main__":
    main()

    # При ранней остановке streaming-датасета PyArrow иногда оставляет
    # фоновый HTTP-reader активным. Все файлы к этому моменту уже закрыты.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
