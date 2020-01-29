#!/usr/bin/env python3

'''
Module that contains all the transition classes.
'''

import collections

import geopandas as gpd
import pandas as pd


class TransitionCell:
    '''
    Cell with gid, name and geometry
    to store the transitions in.
    '''
    def __init__(self, schema, gid, name, geometry, transitions):
        self.schema = schema
        self.gid = gid
        self.name = name
        self.geometry = geometry
        self.transitions = transitions
        self._transition_idx_by_transition_key = {}
        self.len_transitions = len(transitions)

        for idx, transition in enumerate(transitions):
            key = transition.to_key()
            self._transition_idx_by_transition_key[key] = idx

    def add_transition(self, transition):
        '''
        Adds one transition to the list.
        Tries to merge the transitions.
        '''
        key = transition.to_key()
        if key in self._transition_idx_by_transition_key.keys():
            idx_to_insert = self._transition_idx_by_transition_key[key]
            self.transitions[idx_to_insert].n_buildings += \
                transition.n_buildings
        else:
            new_idx = self.len_transitions
            self.transitions.append(transition)
            self.len_transitions += 1
            self._transition_idx_by_transition_key[key] = new_idx

    def to_series(self):
        '''
        Converts the data to a pandas series
        (for export of a list of transition cells
        as geo dataframe).
        '''
        series = pd.Series({
            'gid': self.gid,
            'name': self.name,
            'geometry': self.geometry,
            'schema': self.schema,
            'transitions': {
                'taxonomy': [
                    x.taxonomy
                    for x in self.transitions
                ],
                'from_damage_state': [
                    x.from_damage_state
                    for x in self.transitions
                ],
                'to_damage_state': [
                    x.to_damage_state
                    for x in self.transitions
                ],
                'n_buildings': [
                    x.n_buildings
                    for x in self.transitions
                ],
            },
        })
        return series

    @classmethod
    def from_exposure_cell(cls, exposure_cell):
        '''
        Creates an transition cell by using the
        names, the gid, the schema and the geometry of
        the exposure cell.
        '''
        return cls(
            schema=exposure_cell.schema,
            gid=exposure_cell.gid,
            name=exposure_cell.name,
            geometry=exposure_cell.geometry,
            transitions=[]
        )


TransitionKey = collections.namedtuple(
    'TransitionKey',
    'schema taxonomy from_damage_state to_damage_state'
)


class Transition:
    '''
    Single Transition dataset.
    '''
    def __init__(
            self,
            schema,
            taxonomy,
            from_damage_state,
            to_damage_state,
            n_buildings):
        self.schema = schema
        self.taxonomy = taxonomy
        self.from_damage_state = from_damage_state
        self.to_damage_state = to_damage_state
        self.n_buildings = n_buildings

    def to_key(self):
        return TransitionKey(
            self.schema,
            self.taxonomy,
            self.from_damage_state,
            self.to_damage_state,
        )


class TransitionCellList:
    '''
    List of transition cells.
    '''
    def __init__(self, transition_cells):
        self.transition_cells = transition_cells

    def append(self, transition_cell):
        '''
        Appends the transition cell.
        As this cells are meant to be distinct, there
        is no mechanism for merging here.
        '''
        self.transition_cells.append(transition_cell)

    def to_dataframe(self):
        '''
        Creates a geopandas dataframe, so that the
        data can be saved as geojson.
        '''
        series = [x.to_series() for x in self.transition_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])
