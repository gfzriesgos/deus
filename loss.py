#!/usr/bin/env python3

'''
Module for all the loss related classes.
'''

import json

import geopandas as gpd
import pandas as pd


class LossCellList():
    '''
    List with the spatial cells with the loss data.
    '''
    def __init__(self, loss_cells):
        self._loss_cells = loss_cells

    def get_loss_cells(self):
        '''
        Returns a list of spatial cells with the loss data.
        '''
        return self._loss_cells

    def append(self, loss_cell):
        ''' Append a loss cell.
        There is no logic to merge the cells.
        '''
        self._loss_cells.append(loss_cell)

    def to_dataframe(self):
        '''
        Converts the loss cell list to a dataframe.
        '''
        series = [x.to_series() for x in self._loss_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])


class LossCell():
    '''
    Spatial cell with loss data.
    '''

    def __init__(self, gid, name, geometry, loss_value, loss_unit):
        self._gid = gid
        self._name = name
        self._geometry = geometry
        self._loss_value = loss_value
        self._loss_unit = loss_unit

    def get_gid(self):
        '''
        Returns the gid.
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

    def get_loss_value(self):
        '''
        Returns the computed loss value for this cell.
        '''
        return self._loss_value

    def get_loss_unit(self):
        '''
        Returns the unit for the loss in this cell.
        '''
        return self._loss_unit

    def to_series(self):
        '''
        Converts this cell to a pandas series.
        '''
        series = pd.Series({
            'gid': self._gid,
            'name': self._name,
            'geometry': self._geometry,
            'loss_value': self._loss_value,
            'loss_unit': self._loss_unit,
        })
        return series

    @classmethod
    def from_transition_cell(cls, transition_cell, loss_provider):
        '''
        Creates the loss cell from a transition cell and the
        loss provider.
        '''
        loss_value = 0

        for transition in transition_cell.get_transitions():
            single_loss_value = loss_provider.get_loss(
                schema=transition_cell.get_schema(),
                taxonomy=transition.get_taxonomy(),
                from_damage_state=transition.get_from_damage_state(),
                to_damage_state=transition.get_to_damage_state()
            )
            n_loss_value = single_loss_value * transition.get_n_buildings()

            loss_value += n_loss_value

        return cls(
            gid=transition_cell.get_gid(),
            name=transition_cell.get_name(),
            geometry=transition_cell.get_geometry(),
            loss_value=loss_value,
            loss_unit=loss_provider.get_unit()
        )


class LossProvider():
    '''
    Class to access loss data depending
    on the schema, the taxonomy, the from
    and to damage states.
    '''

    def __init__(self, data, unit=None):
        self._data = data
        self._unit = unit

    def get_loss(
            self,
            schema,
            taxonomy,
            from_damage_state,
            to_damage_state):
        '''
        Returns the loss for the transition.
        '''

        if schema not in self._data:
            raise Exception('schema is not known for loss computation')
        data_for_schema = self._data[schema]['data']

        tax_candidates = [
            x for x in data_for_schema
            if x['taxonomy'] == taxonomy]

        if not tax_candidates:
            raise Exception('no taxonomy candidates found')

        if 'loss_matrix' not in tax_candidates[0]:
            raise Exception('could not found loss matrix for taxonomy')

        loss_matrix = tax_candidates[0]['loss_matrix']
        return loss_matrix[str(from_damage_state)][str(to_damage_state)]

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
