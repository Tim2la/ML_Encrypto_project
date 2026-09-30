from collections import Counter
from math import log


def count_words(text: str) -> Counter[str]:
    # Нормализованный корпус уже разделён пробелами на слова.
    return Counter(text.split())


def segment_text(text: str, word_counts: Counter[str]) -> str:
    """Подбирает вероятные границы слов, не изменяя сами буквы."""
    if not text or not word_counts:
        return text

    total_words = sum(word_counts.values())
    best_scores = [float("-inf")] * (len(text) + 1)
    previous_starts = [0] * (len(text) + 1)
    best_scores[0] = 0.0

    for end in range(1, len(text) + 1):
        for start in range(max(0, end - 25), end):
            word = text[start:end]
            count = word_counts[word]

            # Единичные слова из корпуса часто бывают опечатками, не доверяем им.
            word_score = (
                log(count / total_words)
                if count >= 2
                else -13.0 - 2.0 * len(word)
            )
            candidate_score = best_scores[start] + word_score

            if candidate_score > best_scores[end]:
                best_scores[end] = candidate_score
                previous_starts[end] = start

    words: list[str] = []
    end = len(text)
    while end:
        start = previous_starts[end]
        words.append(text[start:end])
        end = start

    return " ".join(reversed(words))
