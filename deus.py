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
import fragility
import taxonomy

import pandas as pd

def dispatch_intensity_provider(intensity_file):
    return shakemap.Shakemap.from_file(intensity_file).as_intensity_provider()

def dispatch_fragility_function_provider(fragilty_file):
    return fragility.FragilityData.from_file(fragilty_file)

def load_exposure_cell_iterable(exposure_file):
    return exposure.ExposureList.from_file(exposure_file)

def update_exposure(
        exposure_cell,
        intensity_provider,
        fragility_function_provider,
        taxonomy_tester):
    geometry = exposure_cell['geometry']
    centroid = geometry.centroid
    lon = centroid.x
    lat = centroid.y

    intensity, units = intensity_provider.get_nearest(lon, lat)
    value_pga = intensity['PGA']
    units_pga = units['PGA']

    fields_to_copy = ('name', 'geometry', 'gc_id')
    fields_to_ignore_for_n = fields_to_copy + ('index',)

    updated_exposure_cell = pd.Series()
    for field in fields_to_copy:
        updated_exposure_cell[field] = exposure_cell[field]
        for taxonomy in fragility_function_provider:
            for damage_state in taxonomy:
                from_damage_state = damage_state.from_damage_state
                to_damage_state = damage_state.to_damage_state
                # TODO
                # check values and units
                p = damage_state.get_probability_for_intensity(intensity, units)
                # find the numbers of buildings in that class
                n_buildings = compute_n_buildings(
                    exposure_cell,
                    fields_to_ignore_for_n,
                    taxonomy_tester,
                    taxonomy,
                    damage_state)

                n_in_damage_state = p * n_buildings
                new_field_name = taxonomy.get_name() + '_' + from_damage_state + '_' + to_damage_state           
                updated_exposure_cell[new_field_name] = n_in_damage_state

    # it can be the case that the taxonomy must be merged later
    return updated_exposure_cell

def compute_n_buildings(
        exposure_cell,
        fields_to_ignore_for_n,
        taxonomy_tester,
        taxonomy,
        damage_state):

    n_buildings = 0.0
    
    for exposure_cell_field in exposure_cell.keys():
        if exposure_cell_field not in fields_to_ignore_for_n:
        
            if taxonomy_tester.can_use_taxonomy(
                exposure_cell_field,
                    taxonomy.get_name(),
                    damage_state.from_damage_state,
                    damage_state.to_damage_state):
                n_in_class = exposure_cell[exposure_cell_field]
                if type(n_in_class) == str:
                    n_in_class = float(n_in_class)
                if math.isnan(n_in_class):
                    n_in_class = 0.0
                n_buildings += n_in_class
    return n_buildings

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

    taxonomy_tester = taxonomy.TaxonomyTester()

    all_updated_exposure_cells = []

    for exposure_cell in exposure_cell_iterable:
        updated_exposure_cell = update_exposure(
            exposure_cell,
            intensity_provider,
            fragility_function_provider,
            taxonomy_tester)
        all_updated_exposure_cells.append(updated_exposure_cell)

    write_exposure_list(all_updated_exposure_cells, sys.stdout)


if __name__ == '__main__':
    main()
