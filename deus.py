#!/usr/bin/env python3

'''
This is the Damage-Exposure-Update-Service.

Please use -h for usage.
'''

import argparse
import glob
import os

import tellus

import exposure
import fragility
import intensityprovider
import loss
import schemamapping
import shakemap
import transition


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

    worker = tellus.Child(
        intensity_provider,
        fragility_provider,
        exposure_cell_provider,
        loss_provider,
        args
    )
    worker.run()


if __name__ == '__main__':
    main()
