#!/usr/bin/env python3

import io
import tokenize

import lxml.etree as le
import numpy as np
from scipy.spatial import cKDTree

import pdb

class Shakemap():
    def __init__(self, root):
        self._root = root

    def _find_grid_fields(self):
        grid_fields = self._root.findall('{http://earthquake.usgs.gov/eqcenter/shakemap}grid_field')
        return [ShakemapGridField(x) for x in grid_fields]

    def _find_grid_data(self):
        grid_data = self._root.find('{http://earthquake.usgs.gov/eqcenter/shakemap}grid_data')
        return ShakemapGridData(grid_data)

    def _find_grid_specification(self):
        specification = self._root.find('{http://earthquake.usgs.gov/eqcenter/shakemap}grid_specification')
        return ShakemapGridSpecification(specification)
        
    def to_intensity_provider(self):
        grid_fields = self._find_grid_fields()
        grid_data = self._find_grid_data()
        specification = self._find_grid_specification()

        return ShakemapIntensityProvider(grid_fields, specification, grid_data)
        
    @classmethod
    def from_file(cls, file_name):
        xml = le.parse(file_name)
        root = xml.getroot()

        return cls(root)

class ShakemapGridField():
    def __init__(self, xml):
        self._xml = xml

    def get_index(self):
        return self._xml.get('index')

    def get_name(self):
        return self._xml.get('name')

    def get_units(self):
        return self._xml.get('units')

class ShakemapGridSpecification():
    def __init__(self, xml):
        self._xml = xml

    def get_n_lat(self):
        return int(self._xml.get('nlat'))

    def get_n_lon(self):
        return int(self._xml.get('nlon'))
        
class ShakemapGridData():
    def __init__(self, xml):
        self._xml = xml

    def get_text(self):
        return self._xml.text

class ShakemapIntensityProvider():
    def __init__(self, grid_fields, grid_specification, grid_data):
        names = [x.get_name() for x in grid_fields]
        units = {x.get_name(): x.get_units() for x in grid_fields}
        data = {}
        for name in names:
            data[name] = np.zeros(
                grid_specification.get_n_lon() * grid_specification.get_n_lat())
        # it must be tokenized (because of xml processing the newlines
        # may not be consistent)
        tokens = tokenize.tokenize(io.BytesIO(grid_data.get_text().encode('utf-8')).readline)
        index = 0
        rowindex = 0
        for t in tokens:
            # 2 is number
            if t.type == 2:
                if index >= len(names):
                    index = 0
                    rowindex += 1
                name = names[index]
                data[name][rowindex] = float(t.string)
                index += 1
        coords = np.array([[data['LON'][i], data['LAT'][i]] for i in range(len(data['LON']))])
        self._spatial_index = cKDTree(coords)
        self._names = names
        self._data = data
        self._units = units

    def get_nearest(self, lon, lat):
        coord = np.array([lon, lat])
        _, idx = self._spatial_index.query(coord, k=1)

        data = {}
        
        for name in self._names:
            data[name] = self._data[name][idx]

        return data, self._units
