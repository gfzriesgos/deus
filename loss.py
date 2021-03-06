#!/usr/bin/env python3

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
