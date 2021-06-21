#!/usr/bin/env python3

#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright (C) 2019-2021
# - Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
# - Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
# - Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
# - Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)
#
# - Helmholtz Centre Potsdam - GFZ German Research Centre for
#   Geosciences (GFZ, https://www.gfz-potsdam.de) 
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)
#
# Licensed under the Apache License, Version 2.0.
#
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at:
# https://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the Licence for the specific language governing
# permissions and limitations under the Licence.

'''
Module for all the loss related classes.
'''

import json


class LossProvider:
    '''
    Class to access loss data depending
    on the schema, the taxonomy, the from
    and to damage states.
    '''

    def __init__(self, data, unit=None):
        self._data = data
        self._unit = unit

    def get_fallback_replacement_cost(
            self,
            schema,
            taxonomy):
        """
        Return the replacement cost as fallback.

        The idea is to provide the existing information that
        we already have in case that the exposure model itself
        does't provide a replacement cost.
        """
        if schema not in self._data:
            raise Exception('schema is not known for loss computation')
        data_for_schema = self._data[schema]['data']
        if taxonomy not in data_for_schema['replacementCosts'].keys():
            raise Exception(
                'no taxonomy candidates found for %s', repr(taxonomy)
            )

        return data_for_schema['replacementCosts'][taxonomy]

    def get_loss(
            self,
            schema,
            taxonomy,
            from_damage_state,
            to_damage_state,
            replacement_cost):
        '''
        Returns the loss for the transition.
        '''

        if schema not in self._data:
            raise Exception('schema is not known for loss computation')
        data_for_schema = self._data[schema]['data']
        steps = data_for_schema['steps']

        str_from_damage_state = str(from_damage_state)
        str_to_damage_state = str(to_damage_state)

        coeff_from = 0
        if str_from_damage_state in steps.keys():
            coeff_from = steps[str_from_damage_state]

        coeff_to = steps[str_to_damage_state]
        coeff = coeff_to - coeff_from

        return replacement_cost * coeff

    def get_unit(self):
        '''
        Returns the unit of the loss.
        '''
        return self._unit

    @classmethod
    def from_files(cls, files, unit=None):
        '''
        Reads the loss data from a json file.
        '''
        data = {}
        for json_file in files:
            with open(json_file, 'rt') as input_file:
                single_data = json.load(input_file)
                schema = single_data['meta']['id']
                data[schema] = single_data
        return cls(data, unit=unit)
