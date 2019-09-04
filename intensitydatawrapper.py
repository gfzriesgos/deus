#!/usr/bin/env python3

'''
This is the module to provide
an interface and some implementations
for accesing intensity data
either using dicts with lists
or using dataframes or others.


The commom protocol is to support the following methods:

- get_list_x_coordinates():
  Returns a list / series / array of x coordinates
- get_list_y_coordinates():
  Same for the y coordinates
- get_data_columns():
  String list with the names of the columns to read from.
- get_value_for_column_and_index(column, index):
  Reads the value for the column and the index.
  The index will be given by the ckd tree search in the
  intensity provider classes.
- get_unit_for_column_and_index(column, index):
  Similar to te get_value_for_column_and_index method,
  but returns the unit. Can ignore the index if it is the
  same for the whole dataset.
'''

import re


class GeopandasDataFrameWrapper():
    '''
    Wraps a geopandas data frame
    to support the common intensity data protocol.
    This implementation uses prefixes for the value
    and unit columns.
    '''
    def __init__(
            self,
            gdf,
            prefix_value_columns='value_',
            prefix_unit_columns='unit_'):
        self._gdf = gdf
        self._prefix_value_columns = prefix_value_columns
        self._prefix_unit_columns = prefix_unit_columns

    def get_list_x_coordinates(self):
        '''
        Returns a list / series / array of the x coordinates.
        '''
        return self._get_centroid().x

    def get_list_y_coordinates(self):
        '''
        Returns a list / series / array of the y coordinates.
        '''
        return self._get_centroid().y

    def _get_centroid(self):
        return self._gdf['geometry'].centroid

    def get_data_columns(self):
        '''
        Returns a generator to go over all of the
        data columns for the intensity data.
        '''
        for column in self._gdf.columns:
            if column.startswith(self._prefix_value_columns):
                column_without_prefix = re.sub(
                    r'^' + self._prefix_value_columns,
                    '',
                    column
                )
                yield column_without_prefix

    def get_value_for_column_and_index(self, column, index):
        '''
        Returns the value for the column and the index.
        '''
        value_column = self._prefix_value_columns + column
        series = self._gdf.iloc[index]
        return series[value_column]

    def get_unit_for_column_and_index(self, column, index):
        '''
        Returns the unit for the column and the index.
        '''
        unit_column = self._prefix_unit_columns + column
        series = self._gdf.iloc[index]
        return series[unit_column]


class DictWithListDataWrapper():
    '''
    Wrapper for accessing the intensity data using
    a dict with lists for the data
    and an addtional dict for the units.
    '''
    def __init__(self, data, units, x_column, y_column):
        self._data = data
        self._units = units
        self._x_column = x_column
        self._y_column = y_column

    def get_list_x_coordinates(self):
        '''
        Returns a list / series / array of the x coordinates.
        '''
        return self._data[self._x_column]

    def get_list_y_coordinates(self):
        '''
        Returns a list / series / array of the y coordinates.
        '''
        return self._data[self._y_column]

    def get_data_columns(self):
        '''
        Returns a generator to go over all of the
        data columns for the intensity data.
        '''
        for column in self._data.keys():
            if column != self._x_column:
                if column != self._y_column:
                    yield column

    def get_value_for_column_and_index(self, column, index):
        '''
        Returns the value for the column and the index.
        '''
        return self._data[column][index]

    def get_unit_for_column_and_index(self, column, index):
        '''
        Returns the unit for the column and the index.
        This implementation ignores the index.
        '''
        return self._units[column]
