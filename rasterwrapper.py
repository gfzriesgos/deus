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
This is a module to provide wrappers
for different possible apis to deal
with raster data.
'''


class RasterWrapperRio:
    '''
    This is a wrapper using the rasterio
    api to get on the data.
    '''

    def __init__(self, raster_reader):
        self._raster_reader = raster_reader
        self._data = raster_reader.read()

    def is_loaction_in_bbox(self, lon, lat):
        '''
        Tests if a location is in the bounding box of the
        raster.
        '''
        bbox = self._raster_reader.bounds
        if lon < bbox.left:
            return False
        if lon > bbox.right:
            return False
        if lat < bbox.bottom:
            return False
        if lat > bbox.top:
            return False

        return True

    def get_sample(self, lon, lat):
        '''
        Returns the value at the given location.
        Please note: This function does not test if
        the location is in the bounding box of the data.
        Please check that before you query the values!.
        '''
        idx = self._raster_reader.index(lon, lat)
        # at the moment it only supports one band
        return self._data[0, idx[0], idx[1]]


class RasterWrapper:
    '''
    This is a wrapper using the georasters
    api to get on the data.
    '''
    def __init__(self, raster):
        self._raster = raster

    def is_loaction_in_bbox(self, lon, lat):
        '''
        Tests if a location is in the bounding box of the
        raster.
        '''
        if lon < self._raster.xmin:
            return False
        if lon > self._raster.xmax:
            return False
        if lat < self._raster.ymin:
            return False
        if lat > self._raster.ymax:
            return False
        idx = self._raster.map_pixel_location(lon, lat)
        if any(idx < 0):
            return False
        return True

    def get_sample(self, lon, lat):
        '''
        Returns the value at the given location.
        Please note: This function does not test if
        the location is in the bounding box of the data.
        Please check that before you query the values!.
        '''
        return self._raster.map_pixel(lon, lat)
