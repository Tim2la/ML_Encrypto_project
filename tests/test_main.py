from pathlib import Path

import pytest

import main as app
from main import choose_ciphertext_format, choose_language
from src.languages import ENGLISH, RUSSIAN
from src.model_storage import save_model
from src.ngram_model import NGramLanguageModel


def test_choose_russian_language(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "1")

    assert choose_language() == RUSSIAN


def test_choose_english_language(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "2")

    assert choose_language() == ENGLISH


def test_choose_language_rejects_unknown_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "3")

    with pytest.raises(ValueError, match="1 или 2"):
        choose_language()


@pytest.mark.parametrize(
    ("choice", "expected"),
    [("1", False), ("2", True)],
)
def test_choose_ciphertext_format(
    monkeypatch: pytest.MonkeyPatch,
    choice: str,
    expected: bool,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: choice)
    assert choose_ciphertext_format() is expected


def test_choose_ciphertext_format_rejects_unknown_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "3")
    with pytest.raises(ValueError, match="1 или 2"):
        choose_ciphertext_format()


def test_loads_separate_models_for_each_format(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(app, "MODELS_DIRECTORY", tmp_path)
    regular = NGramLanguageModel(n=3, alphabet=RUSSIAN.alphabet + " ")
    regular.fit("АБ ВАБ В")
    compact = NGramLanguageModel(n=3, alphabet=RUSSIAN.alphabet)
    compact.fit("АБВАБВ")
    save_model(regular, tmp_path / "ru_model_3_gramm.pkl")
    save_model(compact, tmp_path / "ru_model_3_compact.pkl")

    assert " " in app.load_language_model(RUSSIAN).alphabet
    assert " " not in app.load_language_model(RUSSIAN, compact=True).alphabet


def test_main_passes_compact_text_to_solver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}
    monkeypatch.setattr(app, "choose_language", lambda: RUSSIAN)
    monkeypatch.setattr(app, "choose_ciphertext_format", lambda: True)
    monkeypatch.setattr(app, "read_ciphertext", lambda: "аб вг!")

    def fake_load_model(language: object, n: int = 3, compact: bool = False) -> object:
        seen["compact"] = compact
        return object()

    def fake_crack_cipher(**kwargs: object) -> tuple[str, dict[str, str], float]:
        seen["ciphertext"] = kwargs["ciphertext"]
        return "АБВГ", {}, -1.0

    monkeypatch.setattr(app, "load_language_model", fake_load_model)
    monkeypatch.setattr(app, "crack_cipher", fake_crack_cipher)
    monkeypatch.setattr(app, "print_decryption_key", lambda *_: None)

    app.main()

    assert seen == {"compact": True, "ciphertext": "АБВГ"}
