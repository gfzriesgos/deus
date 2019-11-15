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
import intensityprovider
import loss
import schemamapping
import shakemap
import transition


COMPUTE_LOSS = True


def create_schema_mapper(current_dir):
    '''
    Creates and returns a schema mapper
    using local mapping files.
    '''
    pattern_to_search_for_tax_files = os.path.join(
        current_dir, 'schema_mapping_data_tax', '*.json')
    tax_mapping_files = glob.glob(pattern_to_search_for_tax_files)

    pattern_to_search_for_ds_files = os.path.join(
        current_dir, 'schema_mapping_data_ds', '*.json')
    ds_mapping_files = glob.glob(pattern_to_search_for_ds_files)

    return (schemamapping
            .SchemaMapper
            .from_taxonomy_and_damage_state_conversion_files(
                tax_mapping_files, ds_mapping_files))


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
        '--updated_exposure_output_file',
        default='output_updated_exposure.json',
        help='Filename for the output with the updated exposure data')
    argparser.add_argument(
        '--transition_output_file',
        default='output_transitions.json',
        help='Filename for the output with the transitions')
    if COMPUTE_LOSS:
        argparser.add_argument(
            '--loss_output_file',
            default='output_loss.json',
            help='Filename for the output with the computed loss')
        current_dir = os.path.dirname(os.path.realpath(__file__))
        loss_data_dir = os.path.join(current_dir, 'loss_data')
        files = glob.glob(os.path.join(loss_data_dir, '*.json'))
        loss_provider = loss.LossProvider.from_files(files, 'USD')

    args = argparser.parse_args()

    intensity_provider = shakemap.Shakemaps.from_file(
        args.intensity_file).to_intensity_provider()
    # add aliases
    # ID for inundation (out of the maximum wave height)
    # SA_01 and SA_03 out of the PGA
    intensity_provider = intensityprovider.AliasIntensityProvider(
        intensity_provider,
        aliases={
            'SA_01': ['PGA'],
            'SA_03': ['PGA'],
            'ID': ['MWH', 'INUN_MEAN_POLY'],
        }
    )
    fragility_provider = fragility.Fragility.from_file(
        args.fragilty_file).to_fragility_provider()
    exposure_cell_provider = exposure.ExposureCellList.from_file(
        file_name=args.exposure_file, schema=args.exposure_schema)

    current_dir = os.path.dirname(os.path.realpath(__file__))

    schema_mapper = create_schema_mapper(current_dir)

    updated_exposure_cells = exposure.ExposureCellList([])
    transition_cells = transition.TransitionCellList([])
    if COMPUTE_LOSS:
        loss_cells = loss.LossCellList([])

    for original_exposure_cell in exposure_cell_provider.exposure_cells:
        mapped_exposure_cell = original_exposure_cell.map_schema(
            target_schema=fragility_provider.schema,
            schema_mapper=schema_mapper
        )
        single_updated_exposure_cell, single_transition_cell = \
            mapped_exposure_cell.update(
                intensity_provider=intensity_provider,
                fragility_provider=fragility_provider
            )

        updated_exposure_cells.append(single_updated_exposure_cell)
        transition_cells.append(single_transition_cell)

        if COMPUTE_LOSS:
            loss_cells.append(
                loss.LossCell.from_transition_cell(
                    single_transition_cell,
                    loss_provider
                )
            )

    write_result(
        args.updated_exposure_output_file,
        updated_exposure_cells)
    write_result(
        args.transition_output_file,
        transition_cells)
    if COMPUTE_LOSS:
        write_result(
            args.loss_output_file,
            loss_cells)


def write_result(
        output_file,
        cells):
    '''
    Write the updated exposure.
    '''
    if os.path.exists(output_file):
        os.unlink(output_file)
    cells.to_dataframe().to_file(output_file, 'GeoJSON')


if __name__ == '__main__':
    main()
