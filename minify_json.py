#!/usr/bin/env python3

"""Script to minify a json file (remove whitespace)."""

import json
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: minify_json.py <file.json>", file=sys.stderr)
        exit(1)

    filename = sys.argv[1]

    with open(filename) as infile:
        data = json.load(infile)

    with open(filename, "w") as outfile:
        json.dumps(data, outfile)


if __name__ == "__main__":
    main()
