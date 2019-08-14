#!/usr/bin/env python3

'''
This is the Damage-Exposure-Update-Service.

Please use -h for usage.
'''

import argparse
import glob
import os

import exposure
import fragility
import shakemap
import taxonomymapping


def update_exposure_cell(exposure_cell,
                         intensity_provider,
                         fragility_provider,
                         taxonomy_mapper):
    '''
    Returns the updated exposure cell.
    '''
    lon, lat = exposure_cell.get_lon_lat_of_centroid()
    intensity, units = intensity_provider.get_nearest(lon=lon, lat=lat)

    updated_cell = exposure_cell.new_prototype()

    for exposure_taxonomy in exposure_cell.get_taxonomies():
        taxonomy = exposure_taxonomy.get_name()
        count = exposure_taxonomy.get_count()
        actual_damage_state = exposure_taxonomy.get_damage_state()

        fragility_taxonomy, mapped_exposure_taxonomy, mapped_damage_state = \
            taxonomy_mapper.find_fragility_taxonomy_and_new_exposure_taxonomy(
                exposure_taxonomy=taxonomy,
                actual_damage_state=actual_damage_state,
                fragility_taxonomies=fragility_provider.get_taxonomies()
            )

        damage_states = fragility_provider.get_damage_states_for_taxonomy(
            fragility_taxonomy)
        damage_states_to_care = [
            ds for ds in damage_states
            if ds.from_state == mapped_damage_state
            and ds.to_state > mapped_damage_state
        ]

        n_not_in_higher_damage_states = count
        for single_damage_state in damage_states_to_care:
            probability = single_damage_state.get_probability_for_intensity(
                intensity, units)
            n_buildings_in_damage_state = probability * count
            n_not_in_higher_damage_states -= n_buildings_in_damage_state

            updated_cell.add_n_for_damage_state(
                mapped_exposure_taxonomy,
                single_damage_state.to_state,
                n_buildings_in_damage_state)

        updated_cell.add_n_for_damage_state(
            mapped_exposure_taxonomy,
            actual_damage_state,
            n_not_in_higher_damage_states)

    return updated_cell


def main():
    '''
    Runs the main method, which reads from
    the files,
    updates each exposure cell individually
    and prints out all of the updated exposure cells.
    '''
    argparser = argparse.ArgumentParser(
        description='Updates the exposure model and the damage ' +
        'classes of the Buildings')
    argparser.add_argument(
        'intensity_file',
        help='File with hazard intensities, for example a shakemap')
    argparser.add_argument(
        'exposure_file',
        help='File with the exposure data')
    argparser.add_argument(
        'fragilty_file',
        help='File with the fragility function data')

    args = argparser.parse_args()

    intensity_provider = shakemap.Shakemap.from_file(
        args.intensity_file).to_intensity_provider()
    fragility_provider = fragility.Fragility.from_file(
        args.fragilty_file).to_fragility_provider()
    exposure_cell_provider = exposure.ExposureCellProvider.from_file(
        args.exposure_file)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    pattern_to_search_for_ds_mappings = os.path.join(
        current_dir, 'mapping_ds_*.json')
    files_ds_mappings = glob.glob(pattern_to_search_for_ds_mappings)
    damage_state_mapper = taxonomymapping.DamageStateMapper.from_files(
        files_ds_mappings)

    taxonomy_mapper = taxonomymapping.TaxonomyMapper(damage_state_mapper)

    updated_exposure_cells = exposure.ExposureCellCollector()

    for exposure_cell in exposure_cell_provider:
        single_updated_exposure_cell = update_exposure_cell(
            exposure_cell=exposure_cell,
            intensity_provider=intensity_provider,
            fragility_provider=fragility_provider,
            taxonomy_mapper=taxonomy_mapper,
        )
        updated_exposure_cells.append(single_updated_exposure_cell)

    print(updated_exposure_cells)


if __name__ == '__main__':
    main()
