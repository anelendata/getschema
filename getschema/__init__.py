#!/usr/bin/env python3
import argparse
import simplejson as json
from .impl import *

# JSON schema follows:
# https://json-schema.org/
COMMAND = "getschema"


def main():
    """
    Entry point
    """
    parser = argparse.ArgumentParser(COMMAND)
    parser.add_argument("data", type=str, help="json record file")
    parser.add_argument("--indent", "-i", default=2, type=int,
                        help="Number of spaces for indentation")
    parser.add_argument("--type", "-t", default="json", type=str,
                        help="Record format (json, yaml, csv)")
    parser.add_argument("--skip", "-s", default=0, type=int,
                        help="Skip first n records. Don't skip the header row.")
    parser.add_argument("--lower", "-l", default=False, action="store_true",
                        help="Convert the keys to lower case'")
    parser.add_argument("--replace_special", "-r", default=None, type=str,
                        help="Replace special characters in the keys with the specified string")
    parser.add_argument("--snakecase", "-n", default=False, action="store_true",
                        help="Convert the keys to 'snake_case'")
    args = parser.parse_args()

    schema = infer_from_file(args.data, args.type.lower(), args.skip,
                             args.lower, args.replace_special, args.snakecase)

    print(json.dumps(schema, indent=args.indent))


if __name__ == "__main__":
    main()
