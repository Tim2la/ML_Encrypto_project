from pathlib import Path

import download_corpus as corpus_module
from src.languages import ENGLISH


def test_download_corpus_writes_text_and_closes_stream(
    monkeypatch,
    tmp_path: Path,
) -> None:
    stream_closed = {"value": False}

    def fake_stream():
        try:
            yield {"text": "First article"}
            yield {"text": "Second article"}
        finally:
            stream_closed["value"] = True

    monkeypatch.setattr(
        corpus_module,
        "load_dataset",
        lambda *args, **kwargs: fake_stream(),
    )
    output_path = corpus_module.download_corpus(
        language=ENGLISH,
        target_characters=10,
        output_directory=tmp_path,
    )

    assert output_path == tmp_path / "wikipedia_en.txt"
    assert output_path.read_text(encoding="utf-8") == "First article"
    assert stream_closed["value"] is True
