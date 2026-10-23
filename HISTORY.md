## History

### 0.2.12 (2026-10-23)
- fix: a null value was inferred as a nullable string, so a field that is an object in
  one record and null in a later one raised "two records differ in types: object
  string". Null now infers as `["null"]` and defers to the other records; a field that
  is null everywhere still becomes the default nullable string.
- fix: an empty object `{}` was inferred as a string. It is an object now; a field that
  is only ever `{}` becomes the default nullable string.
- fix: merging nested objects kept only the later record's properties. Properties are
  now unioned, and array items are merged across every element (not only the first).
- fix: an object-vs-scalar conflict raised only when the object came first; it raises
  in either order now instead of producing a string type that still has properties.
- fix: the `getschema` CLI failed with a NameError (`infer_from_file` not imported).
- ci: GitHub Actions `tests` (Python 3.9-3.12) and tag-triggered `release` (build,
  install smoke test, PyPI Trusted Publishing, post-publish verify).

### 0.2.11 (2025-09-02)
- fix: fix simplejson dependency for singer use

### 0.2.10 (2025-04-08)
- new: default to nullable string when the sample records are all null

### 0.2.9 (2024-07-16)
- new: fix_type function: Option to drop unknown properties

### 0.2.8 (2021-10-26)
- new: fix_type function: Option to convert date to datetime

### 0.2.7 (2021-07-11)
- fix: getschema.fix_type function: A valid null object is rejected

### 0.2.6 (2021-06-29)

- fix: a bug in schema inference where a TypeError is thrown when only a ValueError is currently expected

### 0.2.5 (2021-06-04)

- fix: prevent auto-converting 0, 0.0, '', etc to null
- fix: datetime check during fix_record()

### 0.2.4 (2021-05-28)

- fix: Condition ignores keys with a value of 0 #9
- fix: Incorrect handling of nullable #11

### 0.2.3 (2021-05-25)

- fix: Default type to be string instead of null when no non-null values are found (#7)

### 0.2.2 (2021-05-12)

- fix: Fix JSON file recoginition (#4)
- fix: Don't ignore the field when all records have a field with null value (#3)

### 0.2.1 (2021-05-02)

- fix: Homepage link on pypi

### 0.2.0 (2021-05-02)

- feature: jsonpath support for the record_level parameter in getschema.infer_schema function.
- feature: YAML file support

### 0.1.2 (2020-12-22)

- fix: allow empty dict (Issue #1)

### 0.1.1 (2020-12-05)

- Raise an exception with a clear message when type conflict happens

### 0.1.0 (2020-11-25)

Initial release
