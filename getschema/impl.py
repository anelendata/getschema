#!/usr/bin/env python3
import argparse, csv, datetime, logging, os, re, sys
from dateutil import parser as dateutil_parser
from dateutil.tz import tzoffset
import jsonpath_ng as jsonpath
import simplejson as json
import yaml

# JSON schema follows:
# https://json-schema.org/
COMMAND = "json2schema"

LOGGER = logging.getLogger(__name__)
DEFAULT_TYPE = ["null", "string"]


def _convert_key(old_key, lower=False, replace_special=False, snake_case=False):
    new_key = old_key
    if lower:
        new_key = new_key.lower()
    if replace_special:
        new_key = re.sub('[^ a-zA-Z0-9_]', '_', new_key)
    if snake_case:
        new_key = new_key.strip().replace(" ", "_")
    return new_key


def _get_jsonpath(raw, path):
    jsonpath_expr = jsonpath.parse(path)
    record = [match.value for match in jsonpath_expr.find(raw)]
    return record


def _is_datetime(obj):
    # TODO: This is a very loose regex for date-time.
    return (
        type(obj) is datetime.datetime or
        type(obj) is datetime.date or
        (type(obj) is str and
         re.match("(19|20)\d\d-(0[1-9]|1[012])-([1-9]|0[1-9]|[12][0-9]|3[01])",
                  obj) is not None)
    )


def _do_infer_schema(obj, record_level=None, lower=False,
                     replace_special=False, snake_case=False):
    schema = dict()

    # Go down to the record level if specified
    if record_level:
        obj = _get_jsonpath(obj, record_level)[0]

    if obj is None:
        schema["type"] = ["null"]
    elif type(obj) is dict and obj.keys():
        schema["type"] = ["null", "object"]
        schema["properties"] = dict()
        for key in obj.keys():
            ret = _do_infer_schema(obj[key])
            new_key = _convert_key(
                key, lower=lower, replace_special=replace_special,
                snake_case=snake_case)
            if ret:
                schema["properties"][new_key] = ret

    elif type(obj) is list:
        schema["type"] = ["null", "array"]
        if not obj:
            schema["items"] = None
        # TODO: Check more than the first record
        else:
            ret = _do_infer_schema(
                obj[0], lower=lower, replace_special=replace_special,
                snake_case=snake_case)
            schema["items"] = ret
    else:
        try:
            float(obj)
        except (ValueError, TypeError):
            schema["type"] = ["null", "string"]
            if _is_datetime(obj):
                schema["format"] = "date-time"
        else:
            if type(obj) == bool:
                schema["type"] = ["null", "boolean"]
            elif type(obj) == float or (type(obj) == str and "." in obj):
                schema["type"] = ["null", "number"]
            # Let's assume it's a code such as zipcode if there is a leading 0
            elif type(obj) == int or (type(obj) == str and obj[0] != "0"):
                schema["type"] = ["null", "integer"]
            else:
                schema["type"] = ["null", "string"]
    return schema


def _compare_props(prop1, prop2):
    if not prop2 or prop2.get("type") == ["null"]:
        return prop1
    elif not prop1 or prop1.get("type") == ["null"]:
        return prop2
    prop = prop2
    t1 = prop1["type"]
    t2 = prop2["type"]
    f1 = prop1.get("format")
    f2 = prop2.get("format")
    if t1[1] == "object":
        if t1[1] != t2[1]:
            raise ValueError(
                "While traversing object %s, two records differ in types: %s %s" %
                (prop, t1[1], t2[1]))
        for key in prop["properties"]:
            prop["properties"][key] = _compare_props(
                prop1["properties"].get(key), prop2["properties"].get(key))
    if t1[1] == "array":
        if t1[1] != t2[1]:
            raise ValueError(
                "While traversing array %s, two records differ in types: %s %s" %
                       (prop, t1[1], t2[1]))
        prop["items"] = _compare_props(prop1["items"], prop2["items"])

    numbers = ["integer", "number"]
    if not (t1[1] == t2[1] and f1 == f2):
        if t1[1] in numbers and t2[1] in numbers:
            prop["type"] = ["null", "number"]
        else:
            prop["type"] = ["null", "string"]
            if "format" in prop.keys():
                prop.pop("format")

    return prop


def _infer_from_two(schema1, schema2):
    """
    Compare between currently the most conservative and the new record schemas
    and keep the more conservative one.
    """
    if schema1 is None:
        return schema2
    if schema2 is None:
        return schema1
    schema = schema2
    for key in schema1["properties"]:
        prop1 = schema1["properties"][key]
        prop2 = schema2["properties"].get(key, prop1)
        try:
            schema["properties"][key] = _compare_props(prop1, prop2)
        except Exception as e:
            raise Exception("Key: %s\n%s" % (key, e))
    return schema


def _replace_null_type(schema, path=""):
    new_schema = {}
    new_schema.update(schema)
    if schema["type"] in ("object", ["object"], ["null", "object"]):
        new_schema ["properties"] = {}
        for key in schema.get("properties", {}).keys():
            new_path = path + "." + key
            new_schema["properties"][key] = _replace_null_type(schema["properties"][key], new_path)
    elif schema["type"] == ["null", "array"]:
        if not schema.get("items"):
            new_schema["items"] = {}
        if new_schema["items"].get("type") in (None, "null", ["null"]):
            LOGGER.warning(
                f"{path} is an array without non-null values."
                f"Replacing with the default {DEFAULT_TYPE}")
            new_schema["items"]["type"] = DEFAULT_TYPE
    elif schema["type"] == ["null"]:
        LOGGER.warning(f"{path} contained non-null values only. Replacing with the default {DEFAULT_TYPE}")
        new_schema["type"] = DEFAULT_TYPE
    return new_schema


def _nested_get(input_dict, nested_key):
    internal_dict_value = input_dict
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def _parse_datetime_tz(datetime_str, default_tz_offset=0):
    d = dateutil_parser.parse(datetime_str)
    if not d.tzinfo:
        d = d.replace(tzinfo=tzoffset(None, default_tz_offset))
    return d


def _on_invalid_property(policy, dict_path, obj_type, obj, err_msg):
    if policy == "raise":
        raise Exception(err_msg + " dict_path" + str(dict_path) +
                        " object type: " + obj_type + " object: " + str(obj))
    elif policy == "force":
        cleaned = str(obj)
    elif policy == "null":
        cleaned = None
    else:
        raise ValueError("Unknown policy: %s" % policy)
    return cleaned


def infer_schema(obj, record_level=None,
                 lower=False, replace_special=False, snake_case=False):
    """Infer schema from a given object or a list of objects
    - record_level:
    - lower: Convert the key to all lower case
    - replace_special: Replace letters to _ if not 0-9, A-Z, a-z, _ and -, or " "
    - snake_case: Replace space to _
    """
    if type(obj) is not list:
        obj = [obj]
    if type(obj[0]) is not dict:
        raise ValueError("Input must be a dict object.")
    schema = None
    # Go through the list of objects and find the most safe type assumption
    for o in obj:
        cur_schema = _do_infer_schema(
            o, record_level, lower, replace_special, snake_case)
        # Compare between currently the most conservative and the new record
        # and keep the more conservative.
        schema = _infer_from_two(schema, cur_schema)

    schema["type"] = "object"

    schema = _replace_null_type(schema)

    return schema


def infer_from_json_file(filename, skip=0, lower=False, replace_special=False,
                         snake_case=False):
    with open(filename, "r") as f:
        content = f.read()
    data = json.loads(content)
    if type(data) is list:
        data = data[skip:]
    schema = infer_schema(data, lower=lower, replace_special=replace_special,
                          snake_case=snake_case)

    return schema


def infer_from_yaml_file(filename, skip=0, lower=False, replace_special=False,
                         snake_case=False):
    with open(filename, "r") as f:
        content = f.read()
    data = yaml.load(content, Loader=yaml.FullLoader)
    if type(data) is list:
        data = data[skip:]
    schema = infer_schema(data, lower=lower, replace_special=replace_special,
                          snake_case=snake_case)

    return schema


def infer_from_csv_file(filename, skip=0, lower=False, replace_special=False,
                        snake_case=False):
    with open(filename) as f:
        count = 0
        while count < skip:
            count = count + 1
            f.readline()
        reader = csv.DictReader(f)
        data = [dict(row) for row in reader]
    schema = infer_schema(data, lower=lower, replace_special=replace_special,
                          snake_case=snake_case)

    return schema


def infer_from_file(filename, fmt="json", skip=0, lower=False,
                    replace_special=False, snake_case=False):
    if fmt == "json":
        schema = infer_from_json_file(
            filename, skip, lower, replace_special, snake_case)
    elif fmt == "yaml":
        schema = infer_from_yaml_file(
            filename, skip, lower, replace_special, snake_case)
    elif fmt == "csv":
        schema = infer_from_csv_file(
            filename, skip, lower, replace_special, snake_case)
    else:
        raise KeyError("Unsupported format : " + fmt)
    return schema


def fix_type(obj, schema, dict_path=[], on_invalid_property="raise",
             lower=False, replace_special=False, snake_case=False):
    """Convert the fields into the proper object types.
    e.g. {"number": "1.0"} -> {"number": 1.0}

    - on_invalid_property: ["raise", "null", "force"]
      What to do when the value cannot be converted.
      - raise: Raise exception
      - null: Impute with null
      - force: Keep it as is (string)
    """
    invalid_actions = ["raise", "null", "force"]
    if on_invalid_property not in invalid_actions:
        raise ValueError(
            "on_invalid_property is not one of %s" % invalid_actions)

    obj_type = _nested_get(schema, dict_path + ["type"])
    obj_format = _nested_get(schema, dict_path + ["format"])

    nullable = False
    if obj_type is None:
        if on_invalid_property == "raise":
            raise ValueError("Unknown property found at: %s" % dict_path)
        return None
    if type(obj_type) is list:
        if len(obj_type) > 2:
            raise Exception("Sorry, getschema does not support multiple types")
        nullable = ("null" in obj_type)
        obj_type = obj_type[1] if obj_type[0] == "null" else obj_type[0]

    if obj is None:
        if not nullable:
            if on_invalid_property == "raise":
                raise ValueError("Null object given at %s" % dict_path)
        return None

    # Recurse if object or array types
    if obj_type == "object":
        if type(obj) is not dict:
            raise KeyError("property type (object) Expected a dict object." +
                           "Got: %s %s at %s" % (type(obj), str(obj), str(dict_path)))
        cleaned = dict()
        keys = obj.keys()
        for key in keys:
            ret = fix_type(obj[key], schema, dict_path + ["properties", key],
                           on_invalid_property)
            cleaned[key] = ret
            new_key = _convert_key(key, lower, replace_special, snake_case)
            if key != new_key:
                cleaned[new_key] = cleaned.pop(key)
    elif obj_type == "array":
        assert(type(obj) is list)
        cleaned = list()
        for o in obj:
            ret = fix_type(o, schema, dict_path + ["items"],
                           on_invalid_property)
            if ret is not None:
                cleaned.append(ret)
    else:
        if obj_type == "string":
            if obj is None:
                cleaned = None
            else:
                cleaned = str(obj)
                if obj_format == "date-time":
                    # Just test parsing for now. Not converting to Python's
                    # datetime as re-JSONifying datetime is not straight-foward
                    if not _is_datetime(cleaned):
                        cleaned = _on_invalid_property(
                            on_invalid_property,
                            dict_path, obj_type, cleaned,
                            err_msg="Not in a valid datetime format",
                        )
        elif obj_type == "number":
            if obj is None:
                cleaned = None
            else:
                try:
                    cleaned = float(obj)
                except ValueError as e:
                    cleaned = _on_invalid_property(
                        on_invalid_property, dict_path, obj_type, obj,
                        err_msg=str(e))
        elif obj_type == "integer":
            if obj is None:
                cleaned = None
            else:
                try:
                    cleaned = int(obj)
                except ValueError as e:
                    cleaned = _on_invalid_property(
                        on_invalid_property, dict_path, obj_type, obj,
                        err_msg=str(e))
        elif obj_type == "boolean":
            if obj is None:
                cleaned = None
            elif str(obj).lower() == "true":
                cleaned = True
            elif str(obj).lower() == "false":
                cleaned = False
            else:
                cleaned = _on_invalid_property(
                    on_invalid_property, dict_path, obj_type, obj,
                    err_msg=(str(obj) +
                             " is not a valid value for boolean type"))
        else:
            raise Exception("Invalid type in schema: %s" % obj_type)
    return cleaned
