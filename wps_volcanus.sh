#!/bin/bash

# Run volcanus with the command line arguments for exposure file
# schema string & fragility json file.
# Minify the resulting output too.


set -e

python3 volcanus.py --merged_output_file merged_output.json intensities.shp $@
python3 minify_json.py merged_output.json
