#!/usr/bin/env python3

# Copyright © 2022 Helmholtz Centre Potsdam GFZ German Research Centre for
# Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

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
