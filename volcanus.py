#!/usr/bin/env python3

"""
This is the very same as deus, but specialized to
work with ashfall data.
"""

import argparse
import glob
import os

import tellus

import ashfall
import exposure
import fragility
import intensitydatawrapper
import intensityprovider
import loss
import schemamapping
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
        help='File ashfalls data')
    argparser.add_argument(
        'intensity_column',
        help='Column in the intensity file')
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

    intensity_provider = ashfall.Ashfall.from_file(
        args.intensity_file,
        args.intensity_column
    ).to_intensity_provider()
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
