from src.cipher import RUSSIAN_ALPHABET
from math import log
from collections import Counter
# Counter специальный словарь-счетчик, считает количество повторяющихся объектов и сопостовляет в словарь

# Выделяем граммы
def extract_ngrams(text: str, n: int) -> list[str]:
    if n <= 0:
        raise ValueError("n Должно принадлежать целям положительным")

    if len(text) < n:
        return []
    
    ngrams: list[str] = []

    for start in range(len(text) - n + 1):
        end = start + n
        ngram = text[start:end]
        ngrams.append(ngram)

    return ngrams

# Разделяем на граммы и считаем количество встречающихся грамм
def count_ngrams(text: str, n: int) -> Counter[str]:
    ngrams = extract_ngrams(text, n)
    counts = Counter(ngrams) 

    return counts

# Функция, берем грамм без последнего элемента для вычисления контекста
def count_contexts(text:str, n: int) -> Counter[str]:
    ngrams = extract_ngrams(text, n)
    contexts: list[str] = []

    for ngram in ngrams:
        context = ngram[:-1]
        contexts.append(context)

    return Counter(contexts)

# Вероятность n-грамм со сглаживанием через альфа ()
def ngram_probability(ngram: str,
    ngram_counts: Counter[str],
    context_counts: Counter[str],
    vocabulary_size: int,
    alpha: float = 0.1,) -> float:

    context = ngram[:-1]

    numerator = ngram_counts[ngram] + alpha
    denominator = (context_counts[context] + alpha * vocabulary_size)

    return numerator / denominator

# Класс языковой модели
class NGramLanguageModel:
    def __init__(
        self,
        n: int = 5,
        alpha: float = 0.1,
        alphabet: str = RUSSIAN_ALPHABET + " ") -> None:

        self.n = n
        self.alpha = alpha
        self.alphabet = alphabet

        self.ngram_counts: Counter[str] = Counter()
        self.context_counts: Counter[str] = Counter()
        self.is_trained = False

    # Функция для обучения
    def fit(self, text: str) -> None:
        self.ngram_counts = count_ngrams(text, self.n)
        self.context_counts = count_contexts(text, self.n)
        self.is_trained = True

    def score(self, text: str) -> float:
        if not self.is_trained:
            raise RuntimeError("Сначала необходимо обучить модель")

        ngrams = extract_ngrams(text, self.n)

        if not ngrams:
            raise ValueError("Текст слишком короткий для выбранного n")

        total_log_probability = 0.0

        for ngram in ngrams:
            probability = ngram_probability(
                ngram=ngram,
                ngram_counts=self.ngram_counts,
                context_counts=self.context_counts,
                vocabulary_size=len(self.alphabet),
                alpha=self.alpha,
            )

            total_log_probability += log(probability)

        average_log_probability = (total_log_probability / len(ngrams))

        return average_log_probability