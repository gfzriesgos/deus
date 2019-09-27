#!/usr/bin/env python3

'''
Module that contains all the transition classes.
'''

import geopandas as gpd
import pandas as pd


class TransitionCell():
    '''
    Cell with gid, name and geometry
    to store the transitions in.
    '''
    def __init__(self, schema, gid, name, geometry, transitions):
        self._schema = schema
        self._gid = gid
        self._name = name
        self._geometry = geometry
        self._transitions = transitions

    def get_schema(self):
        '''
        Returns the schema of the taxonomies of the
        transitions.
        '''
        return self._schema

    def get_gid(self):
        '''
        Returns the gid of the cell.
        '''
        return self._gid

    def get_name(self):
        '''
        Returns the name of the cell.
        '''
        return self._name

    def get_geometry(self):
        '''
        Returns the geometry of the cell.
        '''
        return self._geometry

    def get_transitions(self):
        '''
        Returns a list of transitions.
        '''
        return self._transitions

    def add_transition(self, transition):
        '''
        Adds one transition to the list.
        Tries to merge the transitions.
        '''
        idx_to_add = None

        for idx, single_transition in enumerate(self._transitions):
            if single_transition.can_be_merged(transition):
                idx_to_add = idx

        if idx_to_add is not None:
            self._transitions[idx_to_add].merge(transition)
        else:
            self._transitions.append(transition)

    def to_series(self):
        '''
        Converts the data to a pandas series
        (for export of a list of transition cells
        as geo dataframe).
        '''
        series = pd.Series({
            'gid': self._gid,
            'name': self._name,
            'geometry': self._geometry,
            'schema': self._schema,
            'transitions': {
                'taxonomy': [
                    x.get_taxonomy()
                    for x in self._transitions
                ],
                'from_damage_state': [
                    x.get_from_damage_state()
                    for x in self._transitions
                ],
                'to_damage_state': [
                    x.get_to_damage_state()
                    for x in self._transitions
                ],
                'n_buildings': [
                    x.get_n_buildings()
                    for x in self._transitions
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
            schema=exposure_cell.get_schema(),
            gid=exposure_cell.get_gid(),
            name=exposure_cell.get_name(),
            geometry=exposure_cell.get_geometry(),
            transitions=[]
        )


class Transition():
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
        self._schema = schema
        self._taxonomy = taxonomy
        self._from_damage_state = from_damage_state
        self._to_damage_state = to_damage_state
        self._n_buildings = n_buildings

    def get_schema(self):
        '''
        Returns the schema.
        '''
        return self._schema

    def get_taxonomy(self):
        '''
        Returns the taxonomy.
        '''
        return self._taxonomy

    def get_from_damage_state(self):
        '''
        Returns the original damage state.
        '''
        return self._from_damage_state

    def get_to_damage_state(self):
        '''
        Returns the damage state after the transition.
        '''
        return self._to_damage_state

    def get_n_buildings(self):
        '''
        Returns the number of affected buildings.
        '''
        return self._n_buildings

    def can_be_merged(self, other_transition):
        '''
        Tests if the other transition can be merged into
        this one.
        '''
        if self._schema != other_transition.get_schema():
            return False
        if self._taxonomy != other_transition.get_taxonomy():
            return False
        if self._from_damage_state != other_transition.get_from_damage_state():
            return False
        if self._to_damage_state != other_transition.get_to_damage_state():
            return False
        return True

    def merge(self, other_transition):
        '''
        Adds the number of buildings to this transition.
        Here it does not check if the merge is valid or not.
        Please use the can_be_merged method before.
        '''
        self._n_buildings += other_transition.get_n_buildings()


class TransitionCellList():
    '''
    List of transition cells.
    '''
    def __init__(self, transition_cells):
        self._transition_cells = transition_cells

    def get_transition_cells(self):
        '''
        Returns the list of transition cells.
        '''
        return self._transition_cells

    def append(self, transition_cell):
        '''
        Appends the transition cell.
        As this cells are meant to be distinct, there
        is no mechanism for merging here.
        '''
        self._transition_cells.append(transition_cell)

    def to_dataframe(self):
        '''
        Creates a geopandas dataframe, so that the
        data can be saved as geojson.
        '''
        series = [x.to_series() for x in self._transition_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])