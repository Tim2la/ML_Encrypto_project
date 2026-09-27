import pickle # Преобразует Python объект в файл и обратно
from pathlib import Path

from src.ngram_model import NGramLanguageModel


def save_model(
    model: NGramLanguageModel,
    path: str | Path, # Путь можно передать как строкой так и через Path("...")
) -> None:
    model_path = Path(path)

    model_path.parent.mkdir( # Создание корневой папки, если ее еще нет
        parents=True,
        exist_ok=True,
    )

    with model_path.open("wb") as file: # wb открыть для записи и записать бинарные данные
        pickle.dump(model, file) # Сохраняет модель в файл


def load_model(
    path: str | Path,
) -> NGramLanguageModel:
    model_path = Path(path)

    with model_path.open("rb") as file: # открыть для чтения и читать бинарные данные
        model = pickle.load(file) # Выгружает из файла модель

    if not isinstance(model, NGramLanguageModel):
        raise TypeError("Файл не содержит языковую модель")

    return model