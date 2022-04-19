#!/usr/bin/env python3

"""Script to minify a json file inplace (remove whitespace)."""

import json
import sys


def main():
    """Run the main function to minify a json file."""
    if len(sys.argv) < 2:
        print("Usage: minify_json.py <file.json>", file=sys.stderr)
        exit(1)

    filename = sys.argv[1]

    with open(filename) as infile:
        data = json.load(infile)

    with open(filename, "w") as outfile:
        json.dump(data, outfile, separators=(",", ":"))


if __name__ == "__main__":
    main()
