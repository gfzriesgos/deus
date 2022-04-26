#!/usr/bin/env python3

# Copyright © 2021-2022 Helmholtz Centre Potsdam GFZ German Research Centre for
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

"""
Module for all the loss related classes.
"""

import json


class LossProvider:
    """
    Class to access loss data depending
    on the schema, the taxonomy, the from
    and to damage states.
    """

    def __init__(self, data, unit=None):
        self._data = data
        self._unit = unit

    def get_fallback_replacement_cost(self, schema, taxonomy):
        """
        Return the replacement cost as fallback.

        The idea is to provide the existing information that
        we already have in case that the exposure model itself
        does't provide a replacement cost.
        """
        if schema not in self._data:
            raise Exception("schema is not known for loss computation")
        data_for_schema = self._data[schema]["data"]
        if taxonomy not in data_for_schema["replacementCosts"].keys():
            raise Exception(
                "no taxonomy candidates found for %s", repr(taxonomy)
            )

        return data_for_schema["replacementCosts"][taxonomy]

    def get_loss(
        self,
        schema,
        taxonomy,
        from_damage_state,
        to_damage_state,
        replacement_cost,
    ):
        """
        Returns the loss for the transition.
        """

        if schema not in self._data:
            raise Exception("schema is not known for loss computation")
        data_for_schema = self._data[schema]["data"]
        steps = data_for_schema["steps"]

        str_from_damage_state = str(from_damage_state)
        str_to_damage_state = str(to_damage_state)

        coeff_from = 0
        if str_from_damage_state in steps.keys():
            coeff_from = steps[str_from_damage_state]

        coeff_to = steps[str_to_damage_state]
        coeff = coeff_to - coeff_from

        return replacement_cost * coeff

    def get_unit(self):
        """
        Returns the unit of the loss.
        """
        return self._unit

    @classmethod
    def from_files(cls, files, unit=None):
        """
        Reads the loss data from a json file.
        """
        data = {}
        for json_file in files:
            with open(json_file, "rt") as input_file:
                single_data = json.load(input_file)
                schema = single_data["meta"]["id"]
                data[schema] = single_data
        return cls(data, unit=unit)


def combine_losses(
    loss_value, loss_unit, existing_loss_value, existing_loss_unit
):
    """
    Combine the losses of the various runs of deus.

    Normally both should just use the very same loss units, so we can
    add them easily. However, in case we have different units, we
    may need to convert them. So this is the place for it.
    """
    if existing_loss_unit is None or existing_loss_unit == loss_unit:
        combined_loss_value = existing_loss_value + loss_value
        return combined_loss_value, loss_unit
    raise Exception(f"Can't combine {loss_unit} and {existing_loss_unit}")
