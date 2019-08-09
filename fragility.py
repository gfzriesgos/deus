#!/usr/bin/env python3

import json
import math
import re
import pdb

from scipy.stats import lognorm
import numpy as np

class FragilityData():

    def __init__(self, data):
        self._data = data
        self._tax_data = self._prepare_tax_data()

    def _prepare_tax_data(self):
        data_arr = self._data['data']

        data_dict = {}

        for data_arr_element in data_arr:
            taxonomy_name = data_arr_element['taxonomy']
            data_dict[taxonomy_name] = FragilityTaxonomyData(data_arr_element)
        return data_dict

    def __iter__(self):
        for tax_data in self._tax_data.values():
            yield tax_data
            
    def get_taxonomies(self):
        return self._data['meta']['taxonomies']

    def get_data_for_taxonomy(self, taxonomy):
        return self._tax_data[taxonomy]
        
    
    @classmethod
    def from_file(cls, json_file):
        with open(json_file, 'rt') as input_file:
            data = json.load(input_file)
        return cls(data)

class FragilityTaxonomyData():
    def __init__(self, data):
        self._data = data
        self._taxonomy_name = data['taxonomy']
        self._intensity_field = data['imt']
        self._intensity_unit = data['imu']

    def __iter__(self):
        for damage_state in self._get_damage_states():
            mean, stddev = self._get_mean_and_stddev(damage_state)
            from_damage_state, to_damage_state = self._get_from_to_damage_state(damage_state)
            yield DamageState(from_damage_state, to_damage_state, mean, stddev, taxonomy=self)

    def _get_from_to_damage_state(self, damage_state):
        m = re.search(r'^D_(\d+)_(\d+)', damage_state)
        if m:
            from_d = 'D' + m.group(1)
            to_d = 'D' + m.group(2)
            return from_d, to_d
        return 'D0', damage_state
    
    def _get_mean_and_stddev(self, damage_state):
        mean = self._data[damage_state + '_mean']
        stddev = self._data[damage_state + '_stddev']
        return (mean, stddev)

    def _get_damage_states(self):
        return set(
            [self._get_just_damage_state(k) for k in self._data.keys() if self._is_damage_state(k)]
        )

    def _is_damage_state(self, key_in_dict):
        return re.search(r'^D_?\d+(_\d+)?_', key_in_dict)

    def _get_just_damage_state(self, key_in_dict):
        return re.search(r'^(D_?\d+(_\d+)?)_', key_in_dict).group(1)

    def get_name(self):
        return self._data['taxonomy']
    
class DamageState():
    def __init__(self, from_damage_state, to_damage_state, mean, stddev, taxonomy):
        self.from_damage_state = from_damage_state
        self.to_damage_state = to_damage_state
        self._mean = mean
        self._stddev = stddev
        self._taxonomy = taxonomy
        self._f = self._create_function()

    def __repr__(self):
        return 'DamageState(to_state={0}, mean={1}, stddev={2})'.format(repr(self._to_damage_state),
                                                                        repr(self._mean),
                                                                        repr(self._stddev))

    def _create_function(self):
        scale = np.exp(self._mean)
        s = self._stddev
        f = lognorm(scale=scale, s=s)
        return f.cdf
    
    def get_probability_for_intensity(self, intensity, units):
        field = self._taxonomy._intensity_field.upper()
        value = intensity[field]
        unit = units[field]

        if unit != self._taxonomy._intensity_unit:
            # TODO maybe convert it
            raise Exception('Not supported unit')
        
        return self._f(value)
        
