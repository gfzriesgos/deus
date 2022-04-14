#!/bin/bash

# This is the entrypoint for running deus from the wps wrapper.
#
# This will run deus itself with additional cmd arguments for:
# - the current exposure model (filename)
# - the schema (string)
# - the file with the fragility functions (filename)
#
# After it is done it will minify the resulting output with
# the updated exposure, the transitions & the losses.
# (Minifying will remove all unnecessary whitespace).

set -e

python3 deus.py --merged_output_file merged_output.json shakemap_input.xml $@
python3 minify_json.py merged_output.json
python3 create_shapefile.py merged_output.json
