#!/usr/bin/env python3

import argparse
import functools
import math
import io
import tokenize
import pdb
import sys

import geopandas as gpd
import lxml.etree as le
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

class ShakemapIntensityProvider():

    def __init__(self, grid_fields, grid_specification, grid_data):
        names = [x.get_name() for x in grid_fields]
        data = {}
        for name in names:
            data[name] = np.zeros(grid_specification.get_n_lon() * grid_specification.get_n_lat())
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

    def get_nearest(self, lon, lat):
        coord = np.array([lon, lat])
        _, idx = self._spatial_index.query(coord, k=1)
        
        return self._data[self._get_intensity_field_name()][idx]

    def _get_intensity_field_name(self):
        names_to_accept = ('PGA')

        for name in self._names:
            if name in names_to_accept:
                return name
        return None

class ShakemapGrid():
    def __init__(self, root):
        self._root = root

    def find_grid_fields(self):
        grid_fields = self._root.findall('{http://earthquake.usgs.gov/eqcenter/shakemap}grid_field')
        return [ShakemapGridField(x) for x in grid_fields]

    def find_grid_data(self):
        grid_data = self._root.find('{http://earthquake.usgs.gov/eqcenter/shakemap}grid_data')
        return ShakemapGridData(grid_data)

    def find_grid_specification(self):
        specification = self._root.find('{http://earthquake.usgs.gov/eqcenter/shakemap}grid_specification')
        return ShakemapGridSpecification(specification)

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

def dispatch_intensity_provider(intensity_file):
    shakemap_xml = le.parse(intensity_file).getroot()
    shakemap = ShakemapGrid(shakemap_xml)
    shakemap_grid_fields = shakemap.find_grid_fields()
    shakemap_grid_data = shakemap.find_grid_data()
    shakemap_grid_specification = shakemap.find_grid_specification()
    return ShakemapIntensityProvider(shakemap_grid_fields, shakemap_grid_specification, shakemap_grid_data)

def dispatch_fragility_function_provider(fragilty_file):
    pass

def load_exposure_cell_iterable(exposure_file):
    exposure = gpd.GeoDataFrame.from_file(exposure_file)
    for index, row in exposure.iterrows():
        yield row

def update_exposure(exposure_cell, intensity_provider):
    geometry = exposure_cell['geometry']
    centroid = geometry.centroid
    lon = centroid.x
    lat = centroid.y

    intensity = intensity_provider.get_nearest(lon, lat)

    fields_to_copy = ('name', 'geometry', 'gc_id')

    updated_exposure_cell = pd.Series()
    for field in fields_to_copy:
        updated_exposure_cell[field] = exposure_cell[field]
    # it can be the case that the taxonomy must be merged later
    for taxonomy in (x for x in exposure_cell.keys() if x not in fields_to_copy):
        n = exposure_cell[taxonomy]
        if math.isnan(n):
            n = 0
    return updated_exposure_cell


def write_exposure_list(exposure_list, output_stream):
    p = functools.partial(print, file=output_stream)
    dataframe = gpd.GeoDataFrame(exposure_list)
    p(dataframe.to_json())

def main():
    argparser = argparse.ArgumentParser(
        description='Updates the exposure model and the damage classes of the Buildings')
    argparser.add_argument('intensity_file', help='File with hazard intensities, for example a shakemap')
    argparser.add_argument('exposure_file', help='File with the exposure data')
    argparser.add_argument('fragilty_file', help='File with the fragility function data')

    args = argparser.parse_args()

    intensity_provider = dispatch_intensity_provider(args.intensity_file)
    fragility_function_provider = dispatch_fragility_function_provider(args.fragilty_file)
    exposure_cell_iterable = load_exposure_cell_iterable(args.exposure_file)

    all_updated_exposure_cells = []

    for exposure_cell in exposure_cell_iterable:
        updated_exposure_cell = update_exposure(exposure_cell, intensity_provider)
        all_updated_exposure_cells.append(updated_exposure_cell)

    #write_exposure_list(all_updated_exposure_cells, sys.stdout)


if __name__ == '__main__':
    main()
