#!/usr/bin/env python3

import json
import geopandas as gpd

class DamageProvider():

    def __init__(self, data):
        self._data = data

    def get_damage_for_transition(self, building_class, from_damage_state, to_damage_state):
        tax_candidates = [x for x in self._data['data'] if x['taxonomy'] == building_class]
        if not tax_candidates:
            pdb.set_trace()
        conv_matrix = tax_candidates[0]['conv_matrix']
        return conv_matrix[str(from_damage_state)][str(to_damage_state)]

    @classmethod
    def from_file(cls, json_file):
        with open(json_file, 'rt') as input_file:
            data = json.load(input_file)
        return cls(data)

class DamageCellCollector():
    def __init__(self):
        self._elements = []

    def append(self, damage_cell):
        self._elements.append(damage_cell)

    def __str__(self):
        gdf = gpd.GeoDataFrame([x.get_series() for x in self._elements])
        return gdf.to_json()

