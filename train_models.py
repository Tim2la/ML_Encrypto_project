from pathlib import Path

from src.languages import ENGLISH, RUSSIAN, LanguageConfig
from src.model_storage import save_model
from src.ngram_model import NGramLanguageModel
from src.text_processing import normalize_text


PROJECT_ROOT = Path(__file__).resolve().parent # Путь до проекта, до папки
DATA_DIRECTORY = PROJECT_ROOT / "data" 
MODELS_DIRECTORY = PROJECT_ROOT / "models"


def train_language_model(language: LanguageConfig) -> None:
    corpus_path = DATA_DIRECTORY / language.corpus_filename
    raw_text = corpus_path.read_text(encoding="utf-8")
    training_text = normalize_text(raw_text, language.alphabet)

    for i in range(2, 5):
        model = NGramLanguageModel(
            n = i,
            alpha=0.1,
            alphabet=language.alphabet + " ",
        )
        model.fit(training_text)

        model_path = MODELS_DIRECTORY / f"{language.code}_model_{i}_gramm.pkl"
        save_model(model, model_path)

        print(f"{language.display_name}: модель сохранена в {model_path}")


def main() -> None:
    train_language_model(RUSSIAN)
    train_language_model(ENGLISH)


if __name__ == "__main__":
    main()