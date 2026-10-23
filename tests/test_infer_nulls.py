import pytest

import getschema


def _props(schema, *path):
    for p in path:
        schema = schema["properties"][p]
    return schema


@pytest.mark.parametrize("order", [1, -1])
def test_object_or_null_field_in_any_order(order):
    # The shape of Jira's fields.epic: an object on some records, null on others.
    records = [
        {"epic": {"id": 1, "name": "E"}},
        {"epic": None},
        {"epic": {"id": 2, "name": "F", "done": False}},
    ][::order]
    epic = _props(getschema.infer_schema(records), "epic")
    assert epic["type"] == ["null", "object"]
    assert epic["properties"]["id"]["type"] == ["null", "integer"]
    assert epic["properties"]["done"]["type"] == ["null", "boolean"]


def test_null_nested_under_object():
    records = [
        {"a": {"b": {"c": 1}}},
        {"a": {"b": None}},
    ]
    b = _props(getschema.infer_schema(records), "a", "b")
    assert b["type"] == ["null", "object"]
    assert b["properties"]["c"]["type"] == ["null", "integer"]


def test_empty_object_is_an_object():
    records = [
        {"o": {"x": "1"}},
        {"o": {}},
    ]
    o = _props(getschema.infer_schema(records), "o")
    assert o["type"] == ["null", "object"]
    assert "x" in o["properties"]


def test_only_empty_objects_fall_back_to_default():
    schema = getschema.infer_schema([{"o": {}}, {"o": {}}])
    assert _props(schema, "o") == {"type": getschema.impl.DEFAULT_TYPE}


def test_nested_properties_are_unioned():
    records = [
        {"a": {"x": 1}},
        {"a": {"y": "s"}},
    ]
    a = _props(getschema.infer_schema(records), "a")
    assert set(a["properties"]) == {"x", "y"}


def test_array_items_merged_across_elements():
    records = [{"arr": [{"x": 1}, {"y": "s"}, None]}]
    items = _props(getschema.infer_schema(records), "arr")["items"]
    assert items["type"] == ["null", "object"]
    assert set(items["properties"]) == {"x", "y"}


def test_array_of_nulls_falls_back_to_default():
    items = _props(getschema.infer_schema([{"arr": [None, None]}]), "arr")["items"]
    assert items["type"] == getschema.impl.DEFAULT_TYPE


def test_all_null_field_still_defaults_to_nullable_string():
    schema = getschema.infer_schema([{"n": None}, {"n": None}])
    assert _props(schema, "n")["type"] == ["null", "string"]


@pytest.mark.parametrize("order", [1, -1])
def test_object_vs_scalar_conflict_raises_in_any_order(order):
    records = [{"a": {"x": 1}}, {"a": "text"}][::order]
    with pytest.raises(Exception, match="differ in types"):
        getschema.infer_schema(records)


def test_new_key_that_is_null_in_the_later_record():
    # The key appears only in the second record, and only as null there.
    records = [
        {"a": {"x": 1}},
        {"a": {"x": 2, "y": None}},
    ]
    a = _props(getschema.infer_schema(records), "a")
    assert a["properties"]["x"]["type"] == ["null", "integer"]
    assert a["properties"]["y"]["type"] == ["null", "string"]
