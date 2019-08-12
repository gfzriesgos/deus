#!/usr/bin/env python3

'''
This module contains classes to handle
the access to shakemap data.
'''

import io
import tokenize

import lxml.etree as le
import numpy as np
from scipy.spatial import cKDTree


class Shakemap():
    '''
    Class to handle the xml access to
    the shakemap xml elements.
    '''
    def __init__(self, root):
        self._root = root

    def _find_grid_fields(self):
        grid_fields = self._root.findall(
            '{http://earthquake.usgs.gov/eqcenter/shakemap}grid_field')
        return [ShakemapGridField(x) for x in grid_fields]

    def _find_grid_data(self):
        grid_data = self._root.find(
            '{http://earthquake.usgs.gov/eqcenter/shakemap}grid_data')
        return ShakemapGridData(grid_data)

    def _find_grid_specification(self):
        specification = self._root.find(
            '{http://earthquake.usgs.gov/eqcenter/shakemap}grid_specification')
        return ShakemapGridSpecification(specification)

    def to_intensity_provider(self):
        '''
        Returns an instance to access the data point
        that is closest to a given location.
        '''
        grid_fields = self._find_grid_fields()
        grid_data = self._find_grid_data()
        specification = self._find_grid_specification()

        return ShakemapIntensityProvider(
            grid_fields, specification, grid_data)

    @classmethod
    def from_file(cls, file_name):
        '''
        Read the shakemap from an xml file.
        '''
        xml = le.parse(file_name)
        root = xml.getroot()

        return cls(root)


class ShakemapGridField():
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


class ShakemapGridSpecification():
    '''
    Class to give access to the grid specification
    of the shakemap.
    '''
    def __init__(self, xml):
        self._xml = xml

    def get_n_lat(self):
        '''
        Returns the number of distinct latitude points
        in the grid.
        '''
        return int(self._xml.get('nlat'))

    def get_n_lon(self):
        '''
        Returns the number of distinct longitude points
        in the grid.
        '''
        return int(self._xml.get('nlon'))


class ShakemapGridData():
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


class ShakemapIntensityProvider():
    '''
    Class to give access to the nearest value to a given
    location.
    '''
    def __init__(self, grid_fields, grid_specification, grid_data):
        names = [x.get_name() for x in grid_fields]
        units = {x.get_name(): x.get_units() for x in grid_fields}
        data = {}
        for name in names:
            data[name] = np.zeros(
                grid_specification.get_n_lon() *
                grid_specification.get_n_lat())
        # it must be tokenized (because of xml processing the newlines
        # may not be consistent)
        tokens = tokenize.tokenize(
            io.BytesIO(
                grid_data.get_text().encode('utf-8')).readline)
        index = 0
        rowindex = 0
        for token in tokens:
            # 2 is number
            if token.type == 2:
                if index >= len(names):
                    index = 0
                    rowindex += 1
                name = names[index]
                data[name][rowindex] = float(token.string)
                index += 1
        coords = np.array(
            [
                [data['LON'][i],
                 data['LAT'][i]]
                for i in range(len(data['LON']))])
        self._spatial_index = cKDTree(coords)
        self._names = names
        self._data = data
        self._units = units

    def get_nearest(self, lon, lat):
        '''
        Searches for the nearest value in the shakemap to
        the given lon lat location.
        Returns all the data in a dict, as well as all the units.
        Both together are returned as a tuple.
        '''
        coord = np.array([lon, lat])
        _, idx = self._spatial_index.query(coord, k=1)

        data = {}

        for name in self._names:
            data[name] = self._data[name][idx]

        return data, self._units
