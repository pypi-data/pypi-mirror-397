from fr_config._internal.utils import typing as sequence


def test_ensure_list_list():
    value = [1, 2, 3]
    assert sequence.ensure_list(value) == [1, 2, 3]
    value = {1, 2, 3}
    assert sequence.ensure_list(value) == [1, 2, 3]


def test_ensure_list_generator():
    def fn():
        yield 1
        yield 2
        yield 3

    assert sequence.ensure_list(fn()) == [1, 2, 3]


def test_ensure_list_value():
    assert sequence.ensure_list("string") == ["string"]
    assert sequence.ensure_list(b"string") == [b"string"]
    assert sequence.ensure_list(42) == [42]
    assert sequence.ensure_list(None) == []


def test_flatten_value():
    assert list(sequence.flatten("string")) == ["string"]
    assert list(sequence.flatten(42)) == [42]
    assert list(sequence.flatten(None)) == []


def test_flatten_list():
    assert list(sequence.flatten([1, 2, 3])) == [1, 2, 3]


def test_flatten_list_of_lists():
    assert list(sequence.flatten([[1, 2], (3, 4), {5, 6}])) == [1, 2, 3, 4, 5, 6]


def test_first_index():
    assert sequence.first_index is sequence.fi

    assert sequence.fi([1, 2, 3]) == 1
    assert sequence.fi({"a": 1}) == {"a": 1}
    assert sequence.fi(None) == None
    assert sequence.fi("string") == "string"


def test_lsit_index():
    assert sequence.last_index is sequence.li

    assert sequence.li([1, 2, 3]) == 3
    assert sequence.li({"a": 1}) == {"a": 1}
    assert sequence.li(None) == None
    assert sequence.li("string") == "string"
