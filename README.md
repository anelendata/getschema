[![Build Status](https://travis-ci.com/daigotanaka/getschema.svg?branch=master)](https://travis-ci.com/daigotanaka/getschema)

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
  --type TYPE, -t TYPE  Record format (json, csv)
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
- infer_from_csv_file
- fix_type

Example projects using getschema:
- https://github.com/anelendata/tap-rest-api
- https://github.com/anelendata/tap-bigquery

## Original repository

- https://github.com/anelendata/getschema

---

Copyright &copy; 2020 Anelen Co., LLC
