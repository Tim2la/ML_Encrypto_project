from pathlib import Path

from src.model_storage import load_model, save_model
from src.ngram_model import NGramLanguageModel


def test_save_and_load_trained_model(tmp_path: Path) -> None:
    model = NGramLanguageModel(
        n=3,
        alpha=0.1,
        alphabet="АБ ",
    )
    model.fit("АБАБАБАБАБ")

    score_before = model.score("АБАБА")
    model_path = tmp_path / "models" / "test_model.pkl"

    save_model(model, model_path)
    loaded_model = load_model(model_path)

    assert model_path.exists()
    assert loaded_model.is_trained is True
    assert loaded_model.score("АБАБА") == score_before
    