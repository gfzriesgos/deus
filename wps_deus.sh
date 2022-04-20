#!/bin/bash

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
