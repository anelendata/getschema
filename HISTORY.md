## History

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
