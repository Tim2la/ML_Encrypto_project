import pytest

from src.ngram_model import NGramLanguageModel
from src.ngram_model import (count_contexts, count_ngrams, extract_ngrams, ngram_probability,)

def test_extract_ngrams() -> None:
    result = extract_ngrams("ПРИВЕТ", 3)

    assert result == ["ПРИ", "РИВ", "ИВЕ", "ВЕТ"]

def test_extract_ngrams_returns_empty_list_for_short_text() -> None:
    result = extract_ngrams("МИР", 5)

    assert result == []

def test_extract_ngrams_rejects_non_positive_n() -> None:
    with pytest.raises(ValueError):
        extract_ngrams("ПРИВЕТ", 0)

def test_count_ngrams() -> None:
    result = count_ngrams("АБАБА", 2)

    assert result["АБ"] == 2
    assert result["БА"] == 2
    assert len(result) == 2 # Проверяем, что всего два различных грамма

def test_ngram_probability_with_smoothing() -> None:
    text = "АБАБА"

    ngram_counts = count_ngrams(text, 3)
    context_counts = count_contexts(text, 3)

    seen_probability = ngram_probability(
        ngram="АБА",
        ngram_counts=ngram_counts,
        context_counts=context_counts,
        vocabulary_size=2,
        alpha=1.0,
    )

    unseen_probability = ngram_probability(
        ngram="АББ",
        ngram_counts=ngram_counts,
        context_counts=context_counts,
        vocabulary_size=2,
        alpha=1.0,
    )

    assert seen_probability == pytest.approx(0.75)
    assert unseen_probability == pytest.approx(0.25)

def test_language_model_fit_counts_ngrams() -> None:
    model = NGramLanguageModel(n=3)

    model.fit("АБАБА")

    assert model.ngram_counts["АБА"] == 2
    assert model.ngram_counts["БАБ"] == 1
    assert model.context_counts["АБ"] == 2
    assert model.context_counts["БА"] == 1
    assert model.is_trained is True

def test_model_scores_familiar_text_higher() -> None:
    model = NGramLanguageModel(
        n=2,
        alpha=0.1,
        alphabet="АБ ",
    )

    model.fit("АБАБАБАБАБ")

    familiar_score = model.score("АБАБА")
    unfamiliar_score = model.score("ААААА")

    assert familiar_score > unfamiliar_score