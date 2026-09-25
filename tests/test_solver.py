import random

import pytest

from src.cipher import RUSSIAN_ALPHABET, encrypt
from src.languages import ENGLISH_ALPHABET, ENGLISH_FREQUENCY_ORDER
from src.ngram_model import NGramLanguageModel
from src.solver import (
    crack_cipher,
    generate_frequency_key,
    score_key,
    should_accept,
    simulated_annealing,
    solve_with_restarts,
    swap_key_values,
)

def test_swap_key_values_preserves_permutation() -> None:
    original_key = {
        "А": "Х",
        "Б": "П",
        "В": "Т",
    }

    random_generator = random.Random(42)

    new_key = swap_key_values(
        original_key,
        random_generator,
    )

    assert new_key != original_key
    assert set(new_key.keys()) == set(original_key.keys())
    assert set(new_key.values()) == set(original_key.values())

    assert original_key == {
        "А": "Х",
        "Б": "П",
        "В": "Т",
    }

def test_correct_key_gets_higher_score() -> None:
    model = NGramLanguageModel(
        n=2,
        alpha=0.1,
        alphabet="АБВ ",
    )

    plaintext = "ААБААБААБААБ"
    model.fit(plaintext)

    correct_key = {
        "А": "Б",
        "Б": "В",
        "В": "А",
    }

    wrong_key = {
        "А": "А",
        "Б": "Б",
        "В": "В",
    }

    ciphertext = encrypt(
        plaintext,
        correct_key,
    )

    correct_score = score_key(
        ciphertext,
        correct_key,
        model,
    )

    wrong_score = score_key(
        ciphertext,
        wrong_key,
        model,
    )

    assert correct_score > wrong_score

def test_better_candidate_is_always_accepted():
    random_generator = random.Random(42)

    result = should_accept(
        current_score=-2.0,
        candidate_score=-1.5,
        temperature=1.0,
        random_generator=random_generator,
    )

    assert result is True


def test_much_worse_candidate_is_rejected():
    random_generator = random.Random(42)

    result = should_accept(
        current_score=-2.0,
        candidate_score=-10.0,
        temperature=1.0,
        random_generator=random_generator,
    )

    assert result is False

def test_simulated_annealing_does_not_return_worse_key():
    model = NGramLanguageModel(
        n=2,
        alpha=0.1,
        alphabet="АБВ ",
    )

    plaintext = "ААБААБААБААБ"
    model.fit(plaintext)

    encryption_key = {
        "А": "Б",
        "Б": "В",
        "В": "А",
    }

    initial_key = {
        "А": "А",
        "Б": "Б",
        "В": "В",
    }

    ciphertext = encrypt(
        plaintext,
        encryption_key,
    )

    initial_score = score_key(
        ciphertext,
        initial_key,
        model,
    )

    best_key, best_score = simulated_annealing(
        ciphertext=ciphertext,
        initial_key=initial_key,
        model=model,
        iterations=100,
        start_temperature=1.0,
        cooling_rate=0.99,
        seed=42,
    )

    assert best_score >= initial_score
    assert set(best_key.keys()) == set(initial_key.keys())
    assert set(best_key.values()) == set(initial_key.values())

def test_generate_frequency_key():
    ciphertext = "БББААВ"

    key = generate_frequency_key(
        ciphertext=ciphertext,
        alphabet="АБВ",
        frequency_order="АБВ",
    )

    assert key == {
        "А": "Б",
        "Б": "А",
        "В": "В",
    }

def test_solve_with_restarts_preserves_key_and_score():
    model = NGramLanguageModel(
        n=2,
        alpha=0.1,
        alphabet="АБВ ",
    )

    plaintext = "ААБААБААБААБ"
    model.fit(plaintext)

    encryption_key = {
        "А": "Б",
        "Б": "В",
        "В": "А",
    }

    initial_key = {
        "А": "А",
        "Б": "Б",
        "В": "В",
    }

    ciphertext = encrypt(
        plaintext,
        encryption_key,
    )

    initial_score = score_key(
        ciphertext,
        initial_key,
        model,
    )

    best_key, best_score = solve_with_restarts(
        ciphertext=ciphertext,
        initial_key=initial_key,
        model=model,
        restarts=3,
        iterations_per_restart=100,
        seed=42,
    )

    assert best_score >= initial_score
    assert set(best_key.keys()) == set(initial_key.keys())
    assert set(best_key.values()) == set(initial_key.values())

def test_crack_cipher_rejects_text_without_russian_letters():
    model = NGramLanguageModel(
        n=3,
        alpha=0.1,
    )
    model.fit("ЭТО ОБУЧАЮЩИЙ ТЕКСТ")

    with pytest.raises(
        ValueError,
        match="Шифртекст слишком короткий",
    ):
        crack_cipher(
            ciphertext="123 !!!",
            model=model,
        )

def test_crack_cipher_returns_text_key_and_score():
    model = NGramLanguageModel(
        n=2,
        alpha=0.1,
    )
    model.fit(
        "ЭТО ПРОСТОЙ ОБУЧАЮЩИЙ ТЕКСТ " * 10
    )

    decrypted_text, key, score = crack_cipher(
        ciphertext="ФТФ ФЮОБФЮК ФТБФ ФТФ ФЮОБФЮК ФТБФ",
        model=model,
        restarts=1,
        iterations_per_restart=10,
        seed=42,
    )

    assert isinstance(decrypted_text, str)
    assert isinstance(key, dict)
    assert isinstance(score, float)

    assert set(key.keys()) == set(RUSSIAN_ALPHABET)
    assert set(key.values()) == set(RUSSIAN_ALPHABET)


def test_crack_cipher_supports_english_alphabet():
    model = NGramLanguageModel(
        n=2,
        alpha=0.1,
        alphabet=ENGLISH_ALPHABET + " ",
    )
    model.fit(
        "THIS IS A SIMPLE ENGLISH TRAINING TEXT " * 10
    )

    decrypted_text, key, score = crack_cipher(
        ciphertext="UIJT JT B TJNQMF FOHMJTI NFTTBHF",
        model=model,
        alphabet=ENGLISH_ALPHABET,
        frequency_order=ENGLISH_FREQUENCY_ORDER,
        restarts=1,
        iterations_per_restart=10,
        seed=42,
    )

    assert isinstance(decrypted_text, str)
    assert isinstance(score, float)
    assert set(key.keys()) == set(ENGLISH_ALPHABET)
    assert set(key.values()) == set(ENGLISH_ALPHABET)
