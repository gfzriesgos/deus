#!/usr/bin/env python3

'''
Module for handling the exposure data.
'''

import math
import re

import pandas as pd
import geopandas as gpd


class ExposureCellProvider():
    '''
    Class to give access to all of the
    exposure cells.
    '''
    def __init__(self, gdf):
        self._gdf = gdf

    def __iter__(self):
        for _, row in self._gdf.iterrows():
            yield ExposureCell(row)

    @classmethod
    def from_file(cls, file_name):
        '''
        Read the data from a file.
        '''
        gdf = gpd.GeoDataFrame.from_file(file_name)
        return cls(gdf)


class ExposureCellCollector():
    '''
    Class to collection all the (updated) exposure cells.
    Used for output.
    '''
    def __init__(self):
        self._elements = []

    def append(self, exposure_cell):
        '''
        Appends an exposure cell.
        '''
        self._elements.append(exposure_cell)

    def __str__(self):
        gdf = gpd.GeoDataFrame([x.get_series() for x in self._elements])
        return gdf.to_json()


class ExposureCell():
    '''
    Class to represent an exposure cell.
    '''
    def __init__(self, series):
        self._series = series

    def get_series(self):
        '''
        Just returns the series as it is.
        '''
        return self._series

    def get_lon_lat_of_centroid(self):
        '''
        Returns the longitude and latitude of
        the geometry as a tuple.
        '''
        geometry = self._series['geometry']
        centroid = geometry.centroid
        lon = centroid.x
        lat = centroid.y

        return lon, lat

    def new_prototype(self):
        '''
        Creates a new exposure cell that contains
        the same name and geometry as the base object,
        but has no data about the count of buildings for
        a taxonomy.
        '''
        series = pd.Series()
        for field in ExposureCell.get_fields_to_copy():
            series[field] = self._series[field]
        return ExposureCell(series)

    def get_taxonomies(self):
        '''
        Returns all of the taxonomies that are given for the
        exposure cell.
        '''
        result = []
        for field in self._series.keys():
            if field not in ExposureCell.get_fields_to_copy():
                if field not in ExposureCell.get_fields_to_ignore():
                    count = self._series[field]
                    if math.isnan(count):
                        count = 0.0
                    name = field.replace(r'\/', '/')
                    result.append(Taxonomy(name=name, count=count))
        return result

    @staticmethod
    def get_fields_to_copy():
        '''
        Returns the names of fields that should be copied
        on creating a new exposure cell object.
        '''
        return 'name', 'geometry', 'gc_id'

    @staticmethod
    def get_fields_to_ignore():
        '''
        Returns the names of fields that should be ignored
        on searching for the taxonomy fields.
        '''
        return 'index', 'id'

    def add_n_for_damage_state(self, exposure_taxonomy, damage_state, count):
        '''
        Adds the number of buildings for the given taxonomy
        and the given new damage state.
        '''
        exposure_to_set = update_taxonomy_damage_state(
            exposure_taxonomy, damage_state)
        if exposure_to_set not in self._series.keys():
            self._series[exposure_to_set] = 0.0
        self._series[exposure_to_set] += count


def update_taxonomy_damage_state(taxonomy, new_damage_state):
    '''
    Returns the new taxonomy name for the new damage state.
    For example from AA with new damage state 1 the result
    is AA_D1.
    For AA_D1 with new damage state 2 the result is
    AA_D2.
    '''
    match = re.search(r'_D\d$', taxonomy)
    if not match:
        return taxonomy + '_D' + str(new_damage_state)
    return re.sub(r'_D\d$', '_D' + str(new_damage_state), taxonomy)


def get_damage_state_from_taxonomy(taxonomy):
    '''
    Returns the damage state from a given taxonomy string.
    For example for 'AA' the result is 0.
    For 'AA_D1' the result is 1.
    '''

    match = re.search(r'D(\d)$', taxonomy)
    if match:
        return int(match.group(1))
    return 0


class Taxonomy():
    '''
    Class to handle the taxonomy of the exposure.
    '''
    def __init__(self, name, count):
        self._name = name
        self._count = count

    def __eq__(self, other):
        if isinstance(other, Taxonomy):
            return self._name == other.get_name() and \
                    self._count == other.get_count()
        return False

    def get_damage_state(self):
        '''
        Returns the damage state.
        '''
        return get_damage_state_from_taxonomy(self._name)

    def get_name(self):
        '''
        Returns the name of the taxonomy.
        '''
        return self._name

    def get_count(self):
        '''
        Returns the given count of buildings in this class so far.
        '''
        return self._count
