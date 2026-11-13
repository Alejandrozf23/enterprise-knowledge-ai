import json

import pytest

from jsonl_reader import iter_jsonl_objects


def test_iter_jsonl_objects_returns_dicts(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text(
        '{"id": 1}\n{"id": 2}\n',
        encoding="utf-8",
    )

    result = list(iter_jsonl_objects(file_path))

    assert result == [{"id": 1}, {"id": 2}]


def test_iter_jsonl_objects_skips_empty_lines(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text(
        '{"id": 1}\n\n   \n{"id": 2}\n',
        encoding="utf-8",
    )

    result = list(iter_jsonl_objects(file_path))

    assert result == [{"id": 1}, {"id": 2}]


def test_iter_jsonl_objects_raises_value_error_on_invalid_json(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text(
        '{"id": 1}\ninvalid json\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid JSON on line 2"):
        list(iter_jsonl_objects(file_path))


def test_iter_jsonl_objects_skips_invalid_json(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text(
        '{"id": 1}\ninvalid json\n{"id": 2}\n',
        encoding="utf-8",
    )

    result = list(iter_jsonl_objects(file_path, skip_invalid=True))

    assert result == [{"id": 1}, {"id": 2}]


def test_iter_jsonl_objects_raises_type_error_on_non_dict(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text(
        '{"id": 1}\n[1, 2, 3]\n',
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="Expected JSON object on line 2"):
        list(iter_jsonl_objects(file_path))


def test_iter_jsonl_objects_skips_non_dict_records(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text(
        '{"id": 1}\n[1, 2, 3]\n"hello"\n{"id": 2}\n',
        encoding="utf-8",
    )

    result = list(iter_jsonl_objects(file_path, skip_invalid=True))

    assert result == [{"id": 1}, {"id": 2}]


@pytest.mark.parametrize(
    "path",
    [123, None, [], {}],
)
def test_iter_jsonl_objects_rejects_invalid_path_type(path):
    with pytest.raises(TypeError, match="path debe ser str o pathlib.Path"):
        iter_jsonl_objects(path)


@pytest.mark.parametrize(
    "skip_invalid",
    [1, 0, "true", None, [], {}],
)
def test_iter_jsonl_objects_rejects_invalid_skip_invalid_type(
    tmp_path,
    skip_invalid,
):
    file_path = tmp_path / "data.jsonl"

    with pytest.raises(TypeError, match="skip_invalid debe ser bool"):
        iter_jsonl_objects(file_path, skip_invalid=skip_invalid)


def test_iter_jsonl_objects_accepts_string_path(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text('{"id": 1}\n', encoding="utf-8")

    result = list(iter_jsonl_objects(str(file_path)))

    assert result == [{"id": 1}]


def test_iter_jsonl_objects_is_lazy(tmp_path):
    file_path = tmp_path / "data.jsonl"
    file_path.write_text('{"id": 1}\n{"id": 2}\n', encoding="utf-8")

    result = iter_jsonl_objects(file_path)

    assert iter(result) is result
    assert next(result) == {"id": 1}
