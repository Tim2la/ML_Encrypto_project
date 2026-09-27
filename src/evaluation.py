def letter_accuracy(
    original: str,
    predicted: str,
    alphabet: str,
) -> float:
    if len(original) != len(predicted):
        raise ValueError("Длины текстов должны совпадать")

    total_letters = 0
    correct_letters = 0

    for expected, actual in zip(original.upper(), predicted.upper()):
        if expected in alphabet:
            total_letters += 1

            if expected == actual:
                correct_letters += 1

    if total_letters == 0:
        raise ValueError("В исходном тексте нет букв выбранного алфавита")

    return correct_letters / total_letters