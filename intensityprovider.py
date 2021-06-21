#!/usr/bin/env python3

#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright (C) 2019-2021
# - Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
# - Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
# - Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
# - Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)
#
# - Helmholtz Centre Potsdam - GFZ German Research Centre for
#   Geosciences (GFZ, https://www.gfz-potsdam.de) 
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)
#
# Licensed under the Apache License, Version 2.0.
#
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at:
# https://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the Licence for the specific language governing
# permissions and limitations under the Licence.

'''
This is the module to
1. provide the access mechanism for all intensity files and
2. provide methods to convert all intensity files into a
   geojson intensity file format.
'''

import numpy as np
from scipy.spatial import cKDTree


class RasterIntensityProvider:
    '''
    Class to provide the intensities on
    an location by reading from a raster.
    '''

    def __init__(self, raster_wrapper, kind, unit, na_value=0.0):
        self._raster_wrapper = raster_wrapper
        self._kind = kind
        self._unit = unit
        self._na_value = na_value

    def get_nearest(self, lon, lat):
        '''
        Returns a dict with the values and a dict with the
        units of the intensities that the provider has
        on a given location (longitude, latitude).

        It is possible that the point is outside of
        the raster coverage, so
        the value may be zero in that cases.
        '''
        try:
            if self._raster_wrapper.is_loaction_in_bbox(lon, lat):
                value = self._raster_wrapper.get_sample(lon, lat)
            else:
                value = self._na_value
        except IndexError:
            value = self._na_value

        intensities = {self._kind: value}
        units = {self._kind: self._unit}

        return intensities, units


class IntensityProvider:
    '''
    Class for providing the intensities on
    a location.
    '''
    def __init__(self, intensity_data, na_value=0.0):
        self._intensity_data = intensity_data
        self._na_value = na_value
        self._spatial_index = self._build_spatial_index()
        self._max_dist = self._estimate_max_dist()

    def _build_spatial_index(self):
        coords = self._get_coords()
        return cKDTree(coords)

    def _get_coords(self):
        x_coordinates = self._intensity_data.get_list_x_coordinates()
        y_coordinates = self._intensity_data.get_list_y_coordinates()
        coords = np.array(list(zip(x_coordinates, y_coordinates)))
        return coords

    def _estimate_max_dist(self, n_nearest_neighbours=4):
        coords = self._get_coords()
        dists, _ = self._spatial_index.query(coords, k=n_nearest_neighbours)
        dists_without_nearests = dists[:, 1:]

        return np.max(dists_without_nearests)

    def get_nearest(self, lon, lat):
        '''
        Returns a dict with the values and a dict with the
        units of the intensities that the provider has
        on a given location (longitude, latitude).

        It is possible that the point is to far away
        from all of the intensity measurements, so
        the value may be zero in that cases.
        '''
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
                value = self._na_value
            unit = self._intensity_data.get_unit_for_column_and_index(
                column=column,
                index=idx
            )
            intensities[column] = value
            units[column] = unit
        return intensities, units


class StackedIntensityProvider:
    '''
    Class for combining several intensity providers
    into one single instance.
    '''

    def __init__(self, *sub_intensity_providers):
        self._sub_intensity_providers = sub_intensity_providers

    def get_nearest(self, lon, lat):
        '''
        Returns a dict with the values and a dict with the
        units of the intensities that the provider has
        on a given location (longitude, latitude).

        This stacked intensity provider uses a list of
        sub intensity providers to read all the datasets.
        '''
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


class AliasIntensityProvider:
    '''
    Intensity provider that adds intensities as aliases
    for exisiting intensities.

    This is done if one intensity can have several names for
    fragility functions,
    '''
    def __init__(self, inner_intensity_provider, aliases=None):
        if aliases is None:
            aliases = {}
        self._inner_intensity_provider = inner_intensity_provider
        self._aliases = aliases

    def get_nearest(self, lon, lat):
        '''
        Returns the base intensities.
        It also adds intensities under other names.
        '''
        intensities, units = (
            self._inner_intensity_provider.get_nearest(lon, lat)
        )

        for new_intensity_measure in self._aliases:
            possible_intensity_measures = self._aliases[new_intensity_measure]
            # the current behaviour is that later names can overwrite
            # the source columns used before
            # however it is more indented as an overall use
            # case for "Use one of this columns if you have none in the data"
            for given_intensity_measure in possible_intensity_measures:
                if given_intensity_measure in intensities.keys():
                    if new_intensity_measure not in intensities.keys():
                        intensities[new_intensity_measure] = \
                            intensities[given_intensity_measure]
                        units[new_intensity_measure] = \
                            units[given_intensity_measure]

        return intensities, units


class ConversionIntensityProvider:
    '''
    Intensity provider that can convert intensities
    to new intensity measures.

    The AliasIntensityProvider just inserts the intensities and the units as
    they are, here it is possible to rename and convert them to other
    intensities and other units.

    At the moment it supports only single intensity measures to
    be converted into one new, so there is no option
    to compute one new intensity from two or more existing ones
    (so kind a merge).
    '''
    def __init__(
            self,
            inner_intensity_provider,
            from_intensity,
            as_intensity,
            fun):
        self._inner_intensity_provider = inner_intensity_provider
        self._from_intensity = from_intensity
        self._as_intensity = as_intensity
        self._fun = fun

    def get_nearest(self, lon, lat):
        '''
        Adds one intensity measurement with the given conversion function.
        '''
        intensities, units = self._inner_intensity_provider.get_nearest(
            lon,
            lat
        )

        if self._from_intensity in intensities.keys():
            if self._as_intensity not in intensities.keys():
                new_intensity, new_unit = self._fun(
                    intensities[self._from_intensity],
                    units[self._from_intensity]
                )
                intensities[self._as_intensity] = new_intensity
                units[self._as_intensity] = new_unit

        return intensities, units
