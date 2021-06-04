import datetime
import logging
import getschema
import json

LOGGER = logging.getLogger(__name__)


records = [
    {
        "index": 0,
        "array": [
            0.0,
        ],
        "nested_field": {
            "some_prop": 0,
        },
        "boolean_field": True,
        "another_boolean_field": True,
        "number_field": 1,
        "string_field": "a",
        "datetime_field": "2021-06-04",
    },
    {
        "index": 1,
        "array": [
            1,
        ],
        "nested_field": {
            "some_prop": 1,
        },
        "boolean_field": False,
        "another_boolean_field": True,
        "number_field": 0.5,
        "string_field": "b",
        "datetime_field": "2021-06-04T09:00",
    },
]

valid_record = {
    "index": 2,
    "array": [
        1000,
    ],
    "nested_field": {
        "some_prop": -1,
    },
    "datetime_field": "2021-06-01 09:00:00"
}
valid_after_fix = {
    "index": "0",
    "array": [
        "0",
    ],
    "nested_field": {
        "some_prop": "0",
    },
}
invalid_after_fix = {
    "index": "1",
    "array": [
        "a",
    ],
    "nested_field": {
        "some_prop": "1",
    },
}
null_entries = {
    "index": None,
    "array": [
        "1.5",
        None,
    ],
    "nested_field": {
        "some_prop": "3",
    },
    "boolean_field": None,
    "number_field": None,
    "string_field": None,
}
invalid_datetime_record = {
    "index": 2,
    "array": [
        1000,
    ],
    "nested_field": {
        "some_prop": -1,
    },
    "datetime_field": "20"
}
empty_string_record = {
    "index": 2,
    "array": [
        1000,
    ],
    "nested_field": {
        "some_prop": -1,
    },
    "string_field": ""
}


def test_unsupported_schema():
    schema = getschema.infer_schema(records)
    schema["properties"]["index"]["type"] = ["null", "integer", "string"]
    try:
        getschema.fix_type(valid_record, schema)
    except Exception as e:
        assert(str(e).startswith("Sorry, getschema does not support multiple types"))


def test_int_zero():
    schema = getschema.infer_schema(records)

    # This should pass
    getschema.fix_type(valid_record, schema)

    fixed_record = getschema.fix_type(valid_after_fix, schema)
    assert(isinstance(fixed_record["index"], int))
    assert(isinstance(fixed_record["array"][0], float))
    assert(isinstance(fixed_record["nested_field"]["some_prop"], int))

    try:
        fixed_record = getschema.fix_type(invalid_after_fix, schema)
    except Exception as e:
        assert(str(e).startswith("could not convert string to float"))
    else:
        assert False, "It should raise an exception"


def test_datetime():
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["datetime_field"]["type"] ==
           ["null", "string"])
    assert(schema["properties"]["datetime_field"]["format"] == "date-time")
    fixed_record = getschema.fix_type(valid_record, schema)
    assert(isinstance(fixed_record["datetime_field"], str))
    try:
        fixed_record = getschema.fix_type(invalid_datetime_record, schema)
    except Exception as e:
        assert(str(e).startswith("Not in a valid datetime format"))
    else:
        assert False, "It should raise an exception"


def test_empty_string():
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["string_field"]["type"] ==
           ["null", "string"])
    fixed_record = getschema.fix_type(empty_string_record, schema)
    assert(fixed_record["string_field"] == "")
    schema["properties"]["string_field"]["type"] == ["string"]
    fixed_record = getschema.fix_type(empty_string_record, schema)
    assert(fixed_record["string_field"] == "")


def test_preserve_nulls_boolean():
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["boolean_field"]["type"] ==
           ["null", "boolean"])
    fixed_record = getschema.fix_type(null_entries, schema)
    assert(fixed_record["boolean_field"] is None)


def test_preserve_nulls_integer():
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["index"]["type"] == ["null", "integer"])
    fixed_record = getschema.fix_type(null_entries, schema)
    assert(fixed_record["index"] is None)


def test_preserve_nulls_number():
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["number_field"]["type"] == ["null", "number"])
    fixed_record = getschema.fix_type(null_entries, schema)
    assert(fixed_record["number_field"] is None)


def test_preserve_nulls_string():
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["string_field"]["type"] == ["null", "string"])
    fixed_record = getschema.fix_type(null_entries, schema)
    assert(fixed_record["string_field"] is None)


def test_reject_null_boolean():
    schema = getschema.infer_schema(records)
    # This will pass
    _ = getschema.fix_type(null_entries, schema)

    schema["properties"]["boolean_field"]["type"] = ["boolean"]
    try:
        _ = getschema.fix_type(null_entries, schema)
    except Exception as e:
        assert(str(e).startswith("Null object given at"))
    else:
        raise Exception("Supposed to fail with null value")


def test_reject_null_integer():
    schema = getschema.infer_schema(records)
    # This will pass
    _ = getschema.fix_type(null_entries, schema)
    schema["properties"]["index"]["type"] = ["integer"]
    try:
        _ = getschema.fix_type(null_entries, schema)
    except Exception as e:
        assert(str(e).startswith("Null object given at"))
    else:
        raise Exception("Supposed to fail with null value")


def test_reject_null_number():
    schema = getschema.infer_schema(records)
    # This will pass
    _ = getschema.fix_type(null_entries, schema)

    schema["properties"]["number_field"]["type"] = ["number"]
    try:
        _ = getschema.fix_type(null_entries, schema)
    except Exception as e:
        assert(str(e).startswith("Null object given at"))
    else:
        raise Exception("Supposed to fail with null value")


def test_reject_null_string():
    schema = getschema.infer_schema(records)
    # This will pass
    _ = getschema.fix_type(null_entries, schema)

    schema["properties"]["string_field"]["type"] = ["string"]
    try:
        _ = getschema.fix_type(null_entries, schema)
    except Exception as e:
        assert(str(e).startswith("Null object given at"))
    else:
        raise Exception("Supposed to fail with null value")
