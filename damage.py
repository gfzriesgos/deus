#!/usr/bin/env python3

'''
Module to include the
damage provider (loss).
'''

import json
import geopandas as gpd


class DamageProvider():
    '''
    Class to access loss data depending
    on the building class, the from and to
    damage states.
    '''

    def __init__(self, data):
        self._data = data

    def get_damage_for_transition(
            self,
            building_class,
            from_damage_state,
            to_damage_state):
        '''
        Returns the loss for the transition
        from one damage state to another
        on a given building class.
        '''
        tax_candidates = [
            x for x in self._data['data']
            if x['taxonomy'] == building_class]
        loss_matrix = tax_candidates[0]['loss_matrix']
        return loss_matrix[str(from_damage_state)][str(to_damage_state)]

    @classmethod
    def from_file(cls, json_file):
        '''
        Reads the loss data from a json file.
        '''
        with open(json_file, 'rt') as input_file:
            data = json.load(input_file)
        return cls(data)


class DamageCellCollector():
    '''
    Class to collect the cells with the
    computed loss.
    '''
    def __init__(self):
        self._elements = []

    def append(self, damage_cell):
        '''
        Appends a damage cell.
        '''
        self._elements.append(damage_cell)

    def __str__(self):
        gdf = gpd.GeoDataFrame([x.get_series() for x in self._elements])
        return gdf.to_json()
