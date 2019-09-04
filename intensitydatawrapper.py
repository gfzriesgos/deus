#!/usr/bin/env python3

'''
This is the module to provide
an interface and some implementations
for accesing intensity data
either using dicts with lists
or using dataframes or others.
'''

import re

class GeopandasDataFrameWrapper():
    def __init__(self, gdf, prefix_value_columns='value_', prefix_unit_columns='unit_'):
        self._gdf = gdf
        self._prefix_value_columns = prefix_value_columns
        self._prefix_unit_columns = prefix_unit_columns

    def get_list_x_coordinates(self):
        return self._get_centroid().x

    def get_list_y_coordinates(self):
        return self._get_centroid().y

    def _get_centroid(self):
        return self._gdf['geometry'].centroid

    def get_data_columns(self):
        for column in self._gdf.columns:
            if column.startswith(self._prefix_value_columns):
                column_without_prefix = re.sub(r'^' + self._prefix_value_columns, '', column)
                yield column_without_prefix

    def get_value_for_column_and_index(self, column, index):
        value_column = self._prefix_value_columns + column
        series = self._gdf.iloc[index]
        return series[value_column]

    def get_unit_for_column_and_index(self, column, index):
        unit_column = self._prefix_unit_columns + column
        series = self._gdf.iloc[index]
        return series[unit_column]

class DictWithListDataWrapper():
    def __init__(self, data, units, x_column, y_column):
        self._data = data
        self._units = units
        self._x_column = x_column
        self._y_column = y_column

    def get_list_x_coordinates(self):
        return self._data[self._x_column]

    def get_list_y_coordinates(self):
        return self._data[self._y_column]

    def get_data_columns(self):
        for column in self._data.keys():
            if column != self._x_column:
                if column != self._y_column:
                    yield column

    def get_value_for_column_and_index(self, column, index):
        return self._data[column][index]

    def get_unit_for_column_and_index(self, column, index):
        return self._units[column]

