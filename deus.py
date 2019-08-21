#!/usr/bin/env python3

'''
This is the Damage-Exposure-Update-Service.

Please use -h for usage.
'''

import argparse
import glob
import os

import damage
import exposure
import fragility
import shakemap
import schemamapping


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
        'exposure_schema',
        help='The actual schema for the exposure data')
    argparser.add_argument(
        'fragilty_file',
        help='File with the fragility function data')
    argparser.add_argument(
        'damage_file',
        help='File with the damage function data')
    argparser.add_argument(
        '--updated_exposure_output_file',
        default='updated_exposure.json',
        help='Filename for the output with the updated exposure data')
    argparser.add_argument(
        '--transition_output_file',
        default='output_transitions.json',
        help='Filename for the output with the transitions')
    argparser.add_argument(
        '--damage_output_file',
        default='output_damage.json',
        help='Filename for the output with the computed damage')

    args = argparser.parse_args()

    intensity_provider = shakemap.Shakemaps.from_file(
        args.intensity_file).to_intensity_provider()
    fragility_provider = fragility.Fragility.from_file(
        args.fragilty_file).to_fragility_provider()
    exposure_cell_provider = exposure.ExposureCellProvider.from_file(
        args.exposure_file, args.exposure_schema)
    damage_provider = damage.DamageProvider.from_file(
        args.damage_file)

    current_dir = os.path.dirname(os.path.realpath(__file__))

    pattern_to_search_for_bc_mappings = os.path.join(
        current_dir, 'mapping_bc_*.json')
    files_bc_mappings = glob.glob(pattern_to_search_for_bc_mappings)
    building_class_mapper = schemamapping.BuildingClassMapper.from_files(
        files_bc_mappings)

    pattern_to_search_for_ds_mappings = os.path.join(
        current_dir, 'mapping_ds_*.json')
    files_ds_mappings = glob.glob(pattern_to_search_for_ds_mappings)
    damage_state_mapper = schemamapping.DamageStateMapper.from_files(
        files_ds_mappings)

    schema_mapper = schemamapping.SchemaMapper(building_class_mapper,
                                               damage_state_mapper)

    updated_exposure_cells = exposure.ExposureCellCollector()
    transition_cells = exposure.TransitionCellCollector()
    damage_cells = damage.DamageCellCollector()

    for original_exposure_cell in exposure_cell_provider:
        mapped_exposure_cell = original_exposure_cell.map_schema(
            fragility_provider.get_schema(), schema_mapper)
        single_updated_exposure_cell, single_transition_cell = \
            mapped_exposure_cell.update(
                    intensity_provider, fragility_provider)

        updated_exposure_cells.append(single_updated_exposure_cell)
        transition_cells.append(single_transition_cell)

        damage_cells.append(single_transition_cell.to_damage_cell(
            damage_provider))

    updated_exposure_output_file = args.updated_exposure_output_file
    with open(updated_exposure_output_file, 'wt') as output_file_for_exposure:
        print(updated_exposure_cells, file=output_file_for_exposure)

    transition_output_file = args.transition_output_file
    with open(transition_output_file, 'wt') as output_file_for_transitions:
        print(transition_cells, file=output_file_for_transitions)

    with open(args.damage_output_file, 'wt') as output_file_for_damage:
        print(damage_cells, file=output_file_for_damage)


if __name__ == '__main__':
    main()
