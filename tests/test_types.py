import getschema


def test_null_records():
    records = [
        {
            "field": "1",
            "null_field": None,
            "array": [
            ],
            "null_array": [
            ],
            "nested_field": {
                "some_date": "2021-05-25",
                "null_subfield": None,
            },
        },
        {
            "field": "10.0",
            "null_field": None,
            "array": [
                "1",
                "a",
            ],
            "null_array": [
            ],
            "nested_field": {
                "some_date": "2021-05-25",
                "null_subfield": None,
            },
        },
    ]
    schema = getschema.infer_schema(records)
    assert(schema["properties"]["field"]["type"] == ["null", "number"])
    assert(schema["properties"]["null_field"]["type"] == ["null", "string"])
    assert(schema["properties"]["nested_field"]["properties"]["some_date"]["type"] == ["null", "string"])
    assert(schema["properties"]["nested_field"]["properties"]["some_date"]["format"] == "date-time")
    assert(schema["properties"]["nested_field"]["properties"]["null_subfield"]["type"] == ["null", "string"])

