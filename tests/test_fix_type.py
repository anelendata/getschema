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
null_index = {
    "index": None,
    "array": [
        "1",
    ],
    "nested_field": {
        "some_prop": "3",
    },
    "boolean_field": None,
    "another_boolean_field": True,
}



def test_int_zero():
    schema = getschema.infer_schema(records)
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


def test_invalid_obj_type():
    schema = getschema.infer_schema(records)
    schema["properties"]["index"]["type"] = ["null", "integer", "string"]
    try:
        getschema.fix_type(valid_record, schema)
    except Exception as e:
        assert(str(e).startswith("Sorry, getschema does not support multiple types"))
    schema["properties"]["index"]["type"] = ["null", "integer"]
    fixed_record = getschema.fix_type(null_index, schema)
    assert(fixed_record["boolean_field"] is False)
    assert(fixed_record["another_boolean_field"] is True)
    schema["properties"]["index"]["type"] = ["integer"]
    try:
        fixed_record = getschema.fix_type(null_index, schema)
    except Exception as e:
        assert(str(e).startswith("Null object given at"))
