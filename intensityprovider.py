#!/usr/bin/env python3

'''
This is the module to
1. provide the access mechanism for all intensity files and
2. provide methods to convert all intensity files into a
   geojson intensity file format.
'''

import re

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

class IntensityProvider():
    '''
    Class for providing the intensities on
    a location.
    '''
    def __init__(self, gpd):
        self._gpd = gpd
        self._spatial_index = self._build_spatial_index()
        self._max_dist = self._estimate_max_dist()

    def _build_spatial_index(self):
        coords = self._get_coords()
        return cKDTree(coords)

    def _get_coords(self):
        point = self._gpd['geometry'].centroid
        xs = point.x
        ys = point.y
        coords = np.array(list(zip(xs, ys)))
        return coords

    def _estimate_max_dist(self, n_nearest_neighbours=4):
        coords = self._get_coords()
        dists, _ = self._spatial_index.query(coords, k=n_nearest_neighbours)
        dists_without_nearests = dists[:, 1:]

        return np.max(dists_without_nearests)

    def get_nearest(self, lon, lat):
        coord = np.array([lon, lat])
        dist, idx = self._spatial_index.query(coord, k=1)

        intensities = {}
        units = {}

        series = self._gpd.iloc[idx]
        for column in self._gpd.columns:
            if column.startswith('value_'):
                column_without_prefix = re.sub(r'^value_', '', column)
                column_unit = 'unit_' + column_without_prefix
                if dist < self._max_dist:
                    value = series[column]
                else:
                    value = 0.0
                unit = series[column_unit]

                intensities[column_without_prefix] = value
                units[column_without_prefix] = unit
        return intensities, units

class StackedIntensityProvider():
    '''
    Class for combining several intensity providers
    into one single instance.
    '''

    def __init__(self, *sub_intensity_providers):
        self._sub_intensity_providers = sub_intensity_providers

    def get_nearest(self, lon, lat):
        intensities = {}
        units = {}

        for single_sub_intensity_provider in self._sub_intensity_providers:
            sub_intens, sub_units = single_sub_intensity_provider.get_nearest(lon=lon, lat=lat)
            intensities.update(sub_intens)
            units.update(sub_units)
        return intensities, units
