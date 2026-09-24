import random

from math import exp
from collections import Counter
from src.cipher import RUSSIAN_ALPHABET, decrypt
from src.ngram_model import NGramLanguageModel
from src.text_processing import normalize_text

RUSSIAN_FREQUENCY_ORDER = "ОЕАИНТСРВЛКМДПУЯЫЬГЗБЧЙХЖШЮЦЩЭФЪЁ"

def swap_key_values(key: dict[str, str], random_generator: random.Random) -> dict[str, str]:
    if len(key) < 2:
        raise ValueError(
            "Для перестановки нужны минимум две буквы"
        )

    new_key = key.copy()
    letters = list(new_key.keys())

    first_letter, second_letter = random_generator.sample(letters, k=2)

    new_key[first_letter], new_key[second_letter] = (
        new_key[second_letter],
        new_key[first_letter],
    )

    return new_key

def score_key(
    ciphertext: str,
    encryption_key: dict[str, str],
    model: NGramLanguageModel,
) -> float:
    decrypted_text = decrypt(
        ciphertext,
        encryption_key,
    )

    normalized_text = normalize_text(decrypted_text)

    return model.score(normalized_text)

def should_accept(
    current_score: float,
    candidate_score: float,
    temperature: float,
    random_generator: random.Random,
) -> bool:
    if temperature <= 0:
        raise ValueError("Температура должна быть положительной")

    if candidate_score >= current_score:
        return True

    score_difference = candidate_score - current_score
    acceptance_probability = exp(score_difference / temperature)

    random_number = random_generator.random()

    return random_number < acceptance_probability

def generate_frequency_key(
    ciphertext: str,
    alphabet: str = RUSSIAN_ALPHABET,
    frequency_order: str = RUSSIAN_FREQUENCY_ORDER,
) -> dict[str, str]:
    if set(frequency_order) != set(alphabet):
        raise ValueError(
            "Частотный порядок должен содержать все буквы алфавита"
        )

    normalized_text = normalize_text(
        ciphertext,
        alphabet,
    )

    cipher_counts = Counter(
        symbol
        for symbol in normalized_text
        if symbol in alphabet
    )

    cipher_frequency_order = [
        symbol
        for symbol, _ in cipher_counts.most_common()
    ]

    unused_cipher_letters = [
        symbol
        for symbol in alphabet
        if symbol not in cipher_frequency_order
    ]

    cipher_frequency_order.extend(unused_cipher_letters)

    key = dict(
        zip(
            frequency_order,
            cipher_frequency_order,
        )
    )

    return key

def simulated_annealing(
    ciphertext: str,
    initial_key: dict[str, str],
    model: NGramLanguageModel,
    iterations: int = 10_000,
    start_temperature: float = 1.0,
    cooling_rate: float = 0.9995,
    seed: int | None = None,
) -> tuple[dict[str, str], float]:
    if iterations <= 0:
        raise ValueError("Количество итераций должно быть положительным")

    if not 0 < cooling_rate < 1:
        raise ValueError("Коэффициент охлаждения должен находиться между 0 и 1")

    random_generator = random.Random(seed)

    current_key = initial_key.copy()
    current_score = score_key(ciphertext, current_key, model)

    best_key = current_key.copy()
    best_score = current_score

    temperature = start_temperature

    for _ in range(iterations):
        candidate_key = swap_key_values(
            current_key,
            random_generator,
        )

        candidate_score = score_key(
            ciphertext,
            candidate_key,
            model,
        )

        if should_accept(
            current_score=current_score,
            candidate_score=candidate_score,
            temperature=temperature,
            random_generator=random_generator,
        ):
            current_key = candidate_key
            current_score = candidate_score

        if current_score > best_score:
            best_key = current_key.copy()
            best_score = current_score

        temperature = max(
            temperature * cooling_rate,
            1e-12,
        )

    return best_key, best_score

def solve_with_restarts(
    ciphertext: str,
    initial_key: dict[str, str],
    model: NGramLanguageModel,
    restarts: int = 5,
    iterations_per_restart: int = 20_000,
    start_temperature: float = 0.5,
    cooling_rate: float = 0.9995,
    seed: int | None = None,
) -> tuple[dict[str, str], float]:
    if restarts <= 0:
        raise ValueError("Количество перезапусков должно быть положительным")

    best_key = initial_key.copy()
    best_score = score_key(
        ciphertext,
        best_key,
        model,
    )

    for restart_number in range(restarts):
        restart_seed = (
            None
            if seed is None
            else seed + restart_number
        )

        candidate_key, candidate_score = simulated_annealing(
            ciphertext=ciphertext,
            initial_key=initial_key,
            model=model,
            iterations=iterations_per_restart,
            start_temperature=start_temperature,
            cooling_rate=cooling_rate,
            seed=restart_seed,
        )

        if candidate_score > best_score:
            best_key = candidate_key.copy()
            best_score = candidate_score

    return best_key, best_score