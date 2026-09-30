from collections import Counter

from src.word_segmentation import count_words, segment_text


def test_count_words() -> None:
    assert count_words("ЭТО ТЕСТ ЭТО") == Counter({"ЭТО": 2, "ТЕСТ": 1})


def test_segment_text_adds_spaces_without_changing_letters() -> None:
    counts = Counter({"ЭТО": 20, "ТЕСТ": 10})
    result = segment_text("ЭТОТЕСТ", counts)

    assert result == "ЭТО ТЕСТ"
    assert result.replace(" ", "") == "ЭТОТЕСТ"


def test_segment_text_keeps_unknown_letters() -> None:
    counts = Counter({"ЭТО": 20})
    result = segment_text("ЭТОЪ", counts)

    assert result.replace(" ", "") == "ЭТОЪ"
