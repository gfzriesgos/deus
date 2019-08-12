#!/usr/bin/env python3

import collections
import math
import pdb
import re

import pandas as pd
import geopandas as gpd

class ExposureCellProvider():
    def __init__(self, gdf):
        self._gdf = gdf

    def __iter__(self):
        for index, row in self._gdf.iterrows():
            yield ExposureCell(row)

    @classmethod
    def from_file(cls, file_name):
        gdf = gpd.GeoDataFrame.from_file(file_name)
        return cls(gdf)

class ExposureCellCollector():
    def __init__(self):
        self._elements = []

    def append(self, exposure_cell):
        self._elements.append(exposure_cell)

    def __str__(self):
        gdf = gpd.GeoDataFrame([x._series for x in self._elements])
        return gdf.to_json()
    
class ExposureCell():
    def __init__(self, series):
        self._series = series

    def get_lon_lat_of_centroid(self):
        geometry = self._series['geometry']
        centroid = geometry.centroid
        lon = centroid.x
        lat = centroid.y

        return lon, lat

    def new_prototype(self):
        series = pd.Series()
        for field in ExposureCell.get_fields_to_copy():
            series[field] = self._series[field]
        return ExposureCell(series)

    def get_taxonomies(self):
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
        return 'name', 'geometry', 'gc_id'

    @staticmethod
    def get_fields_to_ignore():
        return 'index', 'id'

    def add_n_for_damage_state(self, exposure_taxonomy, damage_state, n):
        exposure_to_set = update_taxonomy_damage_state(exposure_taxonomy, damage_state)
        if not exposure_to_set in self._series.keys():
            self._series[exposure_to_set] = 0.0
        self._series[exposure_to_set] += n


def update_taxonomy_damage_state(taxonomy, new_damage_state):
    m = re.search(r'_D(\d)$', taxonomy)
    if not m:
        return taxonomy + '_D' + str(new_damage_state)
    return re.sub(r'_D(\d)$', '_D' + str(new_damage_state), taxonomy)

def get_damage_state_from_taxonomy(taxonomy):
    m = re.search(r'D(\d)$', taxonomy)
    if m:
        return int(m.group(1))
    return 0
    
    
class Taxonomy():
    def __init__(self, name, count):
        self._name = name
        self._count = count

    def __eq__(self, other):
        if isinstance(other, Taxonomy):
            return self._name == other._name and self._count == other._count
        return False

    def get_damage_state(self):
        return get_damage_state_from_taxonomy(self._name)

    def get_name(self):
        return self._name

    def get_count(self):
        return self._count
