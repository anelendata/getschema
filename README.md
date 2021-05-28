[![Build Status](https://travis-ci.com/anelendata/getschema.svg?branch=main)](https://travis-ci.com/anelendata/getschema)

💥 New: jsonpath support for the record_level parameter in getschema.infer_schema function.

# getschema

Get jsonschema from sample records

Command line usage:
```
usage: getschema [-h] [--indent INDENT] [--type TYPE] [--skip SKIP] [--lower]
                 [--replace_special REPLACE_SPECIAL] [--snakecase]
                 data

positional arguments:
  data                  json record file

optional arguments:
  -h, --help            show this help message and exit
  --indent INDENT, -i INDENT
                        Number of spaces for indentation
  --type TYPE, -t TYPE  Record format (json, yaml, csv)
  --skip SKIP, -s SKIP  Skip first n records. Don't skip the header row.
  --lower, -l           Convert the keys to lower case'
  --replace_special REPLACE_SPECIAL, -r REPLACE_SPECIAL
                        Replace special characters in the keys with the
                        specified string
  --snakecase, -n       Convert the keys to 'snake_case'
getschema file.json
```

Module functions:
(See impl.py)
- infer_schema
- infer_from_json_file
- infer_from_yaml_file
- infer_from_csv_file
- fix_type

Example projects using getschema:
- https://github.com/anelendata/tap-rest-api
- https://github.com/anelendata/tap-bigquery

## Original repository

- https://github.com/anelendata/getschema

# About this project

This project is developed by
ANELEN and friends. Please check out the ANELEN's
[open innovation philosophy and other projects](https://anelen.co/open-source.html)

![ANELEN](https://avatars.githubusercontent.com/u/13533307?s=400&u=a0d24a7330d55ce6db695c5572faf8f490c63898&v=4)
---

Copyright &copy; 2020~ Anelen Co., LLC
