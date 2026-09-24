from pathlib import Path

from datasets import load_dataset


OUTPUT_PATH = Path("data/wikipedia_ru.txt")
TARGET_CHARACTERS = 1_000_000


def main() -> None:
    dataset = load_dataset(
        "wikimedia/wikipedia",
        "20231101.ru",
        split="train",
        streaming=True,
    )

    articles: list[str] = []
    total_characters = 0

    for article in dataset:
        text = article["text"].strip()

        if not text:
            continue

        articles.append(text)
        total_characters += len(text)

        if total_characters >= TARGET_CHARACTERS:
            break

    corpus = "\n".join(articles)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        corpus,
        encoding="utf-8",
    )

    print(f"Собрано статей: {len(articles)}")
    print(f"Собрано символов: {len(corpus)}")
    print(f"Корпус сохранён: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()