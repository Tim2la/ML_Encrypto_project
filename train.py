from pathlib import Path

from src.ngram_model import NGramLanguageModel
from src.text_processing import normalize_text


CORPUS_PATH = Path("data/wikipedia_ru.txt")


def main() -> None:
    raw_text = CORPUS_PATH.read_text(encoding="utf-8")
    training_text = normalize_text(raw_text)

    model = NGramLanguageModel(
        n=5,
        alpha=0.1,
    )

    model.fit(training_text)

    normal_text = normalize_text("ЯЗЫКОВАЯ МОДЕЛЬ ИЗУЧАЕТ ТЕКСТ")

    random_text = normalize_text("ЪЩЦ ЖЭЮФ ЫЪЩЦФ ЖЭЮФ")

    unseen_normal_text = normalize_text("СЕГОДНЯ ХОРОШАЯ ПОГОДА И МЫ ИДЕМ ГУЛЯТЬ")

    unseen_normal_score = model.score(unseen_normal_text)

    normal_score = model.score(normal_text)
    random_score = model.score(random_text)

    print(f"Размер корпуса: {len(training_text)} символов")
    print(f"Оценка обычного текста: {normal_score:.4f}")
    print(f"Оценка случайного текста: {random_score:.4f}")
    print(f"Оценка нового обычного текста: {unseen_normal_score:.4f}")


if __name__ == "__main__":
    main()