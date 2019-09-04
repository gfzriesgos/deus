#!/usr/bin/env python3

'''
This is the module to
1. provide the access mechanism for all intensity files and
2. provide methods to convert all intensity files into a
   geojson intensity file format.
'''

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


class IntensityProvider():
    '''
    Class for providing the intensities on
    a location.
    '''
    def __init__(self, intensity_data):
        self._intensity_data = intensity_data
        self._spatial_index = self._build_spatial_index()
        self._max_dist = self._estimate_max_dist()

    def _build_spatial_index(self):
        coords = self._get_coords()
        return cKDTree(coords)

    def _get_coords(self):
        xs = self._intensity_data.get_list_x_coordinates()
        ys = self._intensity_data.get_list_y_coordinates()
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

        for column in self._intensity_data.get_data_columns():
            if dist <= self._max_dist:
                value = self._intensity_data.get_value_for_column_and_index(
                    column=column,
                    index=idx
                )
            else:
                value = 0.0
            unit = self._intensity_data.get_unit_for_column_and_index(
                column=column,
                index=idx
            )
            intensities[column] = value
            units[column] = unit
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
            sub_intens, sub_units = single_sub_intensity_provider.get_nearest(
                lon=lon,
                lat=lat
            )
            intensities.update(sub_intens)
            units.update(sub_units)
        return intensities, units
