#!/bin/bash

# Run deus with the command line arguments for exposure file
# schema string & fragility json file.
# Minify the resulting output too.

set -e

python3 deus.py --merged_output_file merged_output.json shakemap_input.xml $@
python3 minify_json.py merged_output.json
