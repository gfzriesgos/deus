#!/bin/bash

# This is the entrypoint for running volcanus from the wps wrapper.
#
# This will run volcanus itself with additional cmd arguments for:
# - the current exposure model (filename)
# - the schema (string)
# - the file with the fragility functions (filename)
#
# After it is done it will minify the resulting output with
# the updated exposure, the transitions & the losses.
# (Minifying will remove all unnecessary whitespace).
#
# Remember: Deus works with xml shakemaps, while volcanus uses
# vector data (shapefiles) for the ashfall intensities.


set -e

python3 volcanus.py --merged_output_file merged_output.json intensities.shp $@
python3 minify_json.py merged_output.json
