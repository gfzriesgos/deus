#!/usr/bin/env python3

import collections
import json
import math
import re
import pdb

from scipy.stats import lognorm
import numpy as np

class DamageState():
    def __init__(self,
                 taxonomy,
                 from_state,
                 to_state,
                 mean,
                 stddev,
                 intensity_field,
                 intensity_unit):
        self.taxonomy = taxonomy
        self.from_state = from_state
        self.to_state = to_state
        self.mean = mean
        self.stddev = stddev
        self.intensity_field = intensity_field
        self.intensity_unit = intensity_unit

        self._f = self._create_probability_function()

    def _create_probability_function(self):
        scale = np.exp(self.mean)
        s = self.stddev
        f = lognorm(scale=scale, s=s)
        return f.cdf

    def get_probability_for_intensity(self, intesity, units):
        field = self.intensity_field.upper()
        value = intesity[field]
        unit = units[field]

        if unit != self.intensity_unit:
            raise Exception('Not supported unit')

        return self._f(value)

class Fragility():

    def __init__(self, data):
        self._data = data
    
    @classmethod
    def from_file(cls, json_file):
        with open(json_file, 'rt') as input_file:
            data = json.load(input_file)
        return cls(data)

    def to_fragility_provider(self):
        damage_states_by_taxonomy = collections.defaultdict(list)
        
        for dataset in self._data['data']:
            taxonomy = dataset['taxonomy']
            intensity_field = dataset['imt']
            intensity_unit = dataset['imu']
            for damage_state_mean_key in [
                    k for k in dataset.keys()
                    if k.startswith('D')
                    and k.endswith('_mean')]:
                #
                # the data is in the format
                # D1_mean, D2_mean, D3_mean
                # (as there are is no from data state at the moment)
                # but this code can also handle them the in the way
                # D01, so that it is the damage state from 0 to 1 or
                # D_0_1 or D0_1
                #
                to_state = int(re.search(r'(\d)_mean$', damage_state_mean_key).group(1))
                from_state = int(re.search(r'^D_?(\d)_', damage_state_mean_key).group(1))

                if to_state == from_state:
                    from_state = 0

                mean = dataset[damage_state_mean_key]
                stddev_key = damage_state_mean_key.replace('_mean', '_stddev')
                stddev = dataset[stddev_key]

                damage_state = DamageState(
                    taxonomy=taxonomy,
                    from_state=from_state,
                    to_state=to_state,
                    mean=mean,
                    stddev=stddev,
                    intensity_field=intensity_field,
                    intensity_unit=intensity_unit
                )

                damage_states_by_taxonomy[taxonomy].append(damage_state)
        self._add_damage_states_if_missing(damage_states_by_taxonomy)
        return FraglityProvider(damage_states_by_taxonomy)

    def _add_damage_states_if_missing(self, damage_states_by_taxonomy):
        
        for taxonomy in damage_states_by_taxonomy.keys():
            self._add_damage_states_if_missing_to_dataset_list(
                damage_states_by_taxonomy[taxonomy])
            
    def _add_damage_states_if_missing_to_dataset_list(self, damage_states):
        '''
        If there are data from damage state 0 to 5, 
        but none for 1 to 5, than it they should be added.
        '''
        
        max_damage_state = max([ds.to_state for ds in damage_states])
        for from_damage_state in range(0, max_damage_state):
            for to_damage_state in range(1, max_damage_state+1):
                ds_option = [
                    ds for ds in damage_states
                    if ds.from_state == from_damage_state
                    and ds.to_state == to_damage_state]
                if not ds_option:
                    ds_option_lower = [ds for ds in damage_states
                                       if ds.from_state == from_damage_state - 1
                                       and ds.to_state == to_damage_state]
                    if ds_option_lower:
                        ds_lower = ds_option_lower[0]
                        ds_new = DamageState(
                            taxonomy=ds_lower.taxonomy,
                            from_state=ds_lower.from_state + 1,
                            to_state=ds_lower.to_state,
                            mean=ds_lower.mean,
                            stddev=ds_lower.stddev,
                            intensity_field=ds_lower.intensity_field,
                            intensity_unit=ds_lower.intensity_unit
                        )
                        damage_states.append(ds_new)
        
class FraglityProvider():
    def __init__(self, damage_states_by_taxonomy):
        self._damage_states_by_taxonomy = damage_states_by_taxonomy

    def get_damage_states_for_taxonomy(self, taxonomy):
        return self._damage_states_by_taxonomy[taxonomy]

    def get_taxonomies(self):
        return self._damage_states_by_taxonomy.keys()
