#!/usr/bin/env python3

import argparse
import functools
import math
import io
import tokenize
import pdb
import sys

import shakemap
import exposure

import geopandas as gpd
import lxml.etree as le
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

def dispatch_intensity_provider(intensity_file):
    return shakemap.Shakemap.from_file(intensity_file).as_intensity_provider()

def dispatch_fragility_function_provider(fragilty_file):
    pass

def load_exposure_cell_iterable(exposure_file):
    return exposure.ExposureList.from_file(exposure_file)

def update_exposure(exposure_cell, intensity_provider):
    geometry = exposure_cell['geometry']
    centroid = geometry.centroid
    lon = centroid.x
    lat = centroid.y

    intensity, units = intensity_provider.get_nearest(lon, lat)
    value_pga = intensity['PGA']
    units_pga = units['PGA']

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

    exposure_list = exposure.ExposureList.from_list(exposure_list)
    json = exposure_list.to_json()

    p(json)
    
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

    write_exposure_list(all_updated_exposure_cells, sys.stdout)


if __name__ == '__main__':
    main()
