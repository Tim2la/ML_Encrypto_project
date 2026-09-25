from dataclasses import dataclass


RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
RUSSIAN_FREQUENCY_ORDER = "ОЕАИНТСРВЛКМДПУЯЫЬГЗБЧЙХЖШЮЦЩЭФЪЁ"

ENGLISH_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ENGLISH_FREQUENCY_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    display_name: str
    alphabet: str
    frequency_order: str
    corpus_filename: str
    wikipedia_config: str


RUSSIAN = LanguageConfig(
    code="ru",
    display_name="Русский",
    alphabet=RUSSIAN_ALPHABET,
    frequency_order=RUSSIAN_FREQUENCY_ORDER,
    corpus_filename="wikipedia_ru.txt",
    wikipedia_config="20231101.ru",
)

ENGLISH = LanguageConfig(
    code="en",
    display_name="English",
    alphabet=ENGLISH_ALPHABET,
    frequency_order=ENGLISH_FREQUENCY_ORDER,
    corpus_filename="wikipedia_en.txt",
    wikipedia_config="20231101.en",
)

LANGUAGES_BY_CHOICE = {
    "1": RUSSIAN,
    "2": ENGLISH,
}

LANGUAGES_BY_CODE = {
    language.code: language
    for language in LANGUAGES_BY_CHOICE.values()
}
