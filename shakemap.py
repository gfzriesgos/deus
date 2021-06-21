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
This module contains classes to handle
the access to shakemap data.
'''

import collections
import io
import tokenize

import lxml.etree as le
from lxml.etree import XMLParser

import intensitydatawrapper
import intensityprovider


class Shakemaps:
    '''
    Factory class for reading shakemaps.
    '''
    @staticmethod
    def from_file(file_name):
        '''
        Read the shakemap from an xml file.
        '''
        huge_parser = XMLParser(
            encoding='utf-8',
            recover=True,
            huge_tree=True
        )
        xml = le.parse(file_name, huge_parser)
        root = xml.getroot()

        return EqShakemap(root)


class EqShakemap:
    '''
    Class to handle the xml access to
    the shakemap xml elements.
    '''
    def __init__(self, root):
        self._root = root

    def _find_grid_fields(self):
        grid_fields = self._root.findall(
            '{http://earthquake.usgs.gov/eqcenter/shakemap}grid_field')
        # fallback if namespace is not proper
        if len(grid_fields) == 0:
            grid_fields = self._root.findall('grid_field')

        return [ShakemapGridField(x) for x in grid_fields]

    def _find_grid_data(self):
        grid_data = self._root.find(
            '{http://earthquake.usgs.gov/eqcenter/shakemap}grid_data')
        # fallback if namespace is not proper
        if grid_data is None:
            grid_data = self._root.find('grid_data')
        return ShakemapGridData(grid_data)

    def _find_lon_lat_spacing(self):
        grid_specification = self._root.find(
            '{http://earthquake.usgs.gov/eqcenter/shakemap}grid_specification')
        nominal_lat_spacing = grid_specification.get('nominal_lat_spacing')
        nominal_lon_spacing = grid_specification.get('nominal_lon_spacing')

        return float(nominal_lon_spacing), float(nominal_lat_spacing)

    def to_intensity_provider(self):
        '''
        Returns an instance to access the data point
        that is closest to a given location.
        '''
        data, units = read_shakemap_data_and_units(
            grid_fields=self._find_grid_fields(),
            grid_data=self._find_grid_data())

        wrapped_data = intensitydatawrapper.DictWithListDataWrapper(
            data=data,
            units=units,
            possible_x_columns=['LON', 'CENTROID_LON'],
            possible_y_columns=['LAT', 'CENTROID_LAT'],
        )

        return intensityprovider.IntensityProvider(intensity_data=wrapped_data)


class ShakemapGridField:
    '''
    Class to represent a shakemap
    grid field.
    '''
    def __init__(self, xml):
        self._xml = xml

    def get_index(self):
        '''
        Returns the index value of the field (one-based).
        '''
        return self._xml.get('index')

    def get_name(self):
        '''
        Returns the name of the field.
        '''
        return self._xml.get('name')

    def get_units(self):
        '''
        Returns the unit of the field.
        '''
        return self._xml.get('units')


class ShakemapGridData:
    '''
    Class for the xml element with the grid data.
    '''
    def __init__(self, xml):
        self._xml = xml

    def get_text(self):
        '''
        Returns the text of the data.
        This is a tsv content without header (as this is in the
        grid fields).
        '''
        return self._xml.text


def read_shakemap_data_from_str(grid_data_text):
    '''
    Helper to work with the tokens.
    Can work with both strings and floats.
    '''
    # it must be tokenized (because of xml processing the newlines
    # may not be consistent)
    tokens = tokenize.tokenize(
        io.BytesIO(
            grid_data_text.encode('utf-8')).readline)
    token_before = None
    for token in tokens:
        # 2 is number
        if token.type == 2:
            value = float(token.string)
            if token_before is not None and token_before.string == '-':
                value = -1 * value
            yield value
        # 3 is str
        elif token.type == 3:
            raw_value = token.string
            # remove quotes around
            value = raw_value[1:-1]
            yield value
        # take care about the before token for negative numbers
        token_before = token


def read_shakemap_data_and_units(grid_fields, grid_data):
    '''
    Function to read the grid_data and the grid fields.
    Returns a dict with the values (in lists) and a dict
    with units for the different fields.
    '''
    names = [x.get_name().upper() for x in grid_fields]
    units = {x.get_name().upper(): x.get_units() for x in grid_fields}
    data = collections.defaultdict(list)
    values = read_shakemap_data_from_str(grid_data.get_text())
    for idx, value in enumerate(values):
        name_idx = idx % len(names)
        name = names[name_idx]
        data[name].append(value)
    return data, units
