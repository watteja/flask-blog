import pytest

from dailypush.utils import multireplace


@pytest.mark.parametrize(
    ("text", "replacements", "ignore_case", "text_replaced"),
    (
        ("The Lord of the Rings", {"the": "a"}, True, "a Lord of a Rings"),
        ("The Lord of the Rings", {"the": "a"}, False, "The Lord of a Rings"),
        ("The Lord of the Rings", {}, True, "The Lord of the Rings"),
    ),
)
def test_multireplace(text, replacements, ignore_case, text_replaced):
    assert text_replaced == multireplace(text, replacements, ignore_case)
