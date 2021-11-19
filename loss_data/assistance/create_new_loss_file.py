#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
This is a helper script to transform the
existing replacement cost files.
The old data are explicit about every taxonomy,
but it just follows a single schema.

For SARA:
The replacement cost from D0 to D1 is always 0.02
times the replacement for D0 to D4.
Same is true for D1, D2, D3, ... and other schemas.
The replacement costs for transitions from D1
to D2 can be computed out of this steps as well.

For the future we want to read the replacement costs
per building out of the exposure model.

However we can also include some fallback data in case
that the exposure model has no replacement cost data.
"""

import json
import glob
import os


def read_json(filename):
    with open(filename) as inputfile:
        return json.load(inputfile)


loss_steps = {
    "SARA_v1.0": {
        "steps": {"1": 0.02, "2": 0.1, "3": 0.5, "4": 1.0},
        "get_max": lambda x: x["0"]["4"],
    },
    "Torres_Corredor_et_al_2017": {
        "steps": {"1": 0.16666666666666669, "2": 0.5, "3": 1},
        "get_max": lambda x: x["0"]["3"],
    },
    "Mavrouli_et_al_2014": {
        "steps": {
            "2": 0.2,
            "3": 0.6,
            "4": 1,
        },
        "get_max": lambda x: x["0"]["4"],
    },
    "SUPPASRI2013_v2.0": {
        "steps": {
            "1": 0.05,
            "2": 0.15,
            "3": 0.45,
            "4": 0.65,
            "5": 0.85,
            "6": 1,
        },
        "get_max": lambda x: x["0"]["6"],
    },
}

for filename in glob.glob("old/*.json"):
    data = read_json(filename)
    meta_id = data["meta"]["id"]

    if meta_id in loss_steps.keys():
        replacement_costs = {}

        for tax_data_set in data["data"]:
            max_value = loss_steps[meta_id]["get_max"](tax_data_set["loss_matrix"])
            taxonomy = tax_data_set["taxonomy"]

            replacement_costs[taxonomy] = max_value

        out_dict = {
            "meta": {"id": meta_id},
            "data": {
                "steps": loss_steps[meta_id]["steps"],
                "replacementCosts": replacement_costs,
            },
        }

        output_filename = os.path.basename(filename)
        with open(output_filename, "w") as outfile:
            json.dump(out_dict, outfile, indent=4)
