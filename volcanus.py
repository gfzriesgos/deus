#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright (C) 2019-2021
# - Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
# - Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
# - Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
# - Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)
#
# - Helmholtz Centre Potsdam - GFZ German Research Centre for
#   Geosciences (GFZ, https://www.gfz-potsdam.de) 
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)
#
# Licensed under the Apache License, Version 2.0.
#
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at:
# https://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the Licence for the specific language governing
# permissions and limitations under the Licence.

"""
This is the very same as deus, but specialized to
work with ashfall data.
"""

import argparse
import glob
import os

import tellus

import ashfall
import fragility
import gpdexposure
import intensitydatawrapper
import intensityprovider
import loss
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
    argparser.add_argument(
        '--merged_output_file',
        default='output_merged.json',
        help='Filename for the merged output from all others')
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
    old_exposure = gpdexposure.read_exposure(args.exposure_file)

    worker = tellus.Child(
        intensity_provider,
        fragility_provider,
        old_exposure,
        args.exposure_schema,
        loss_provider,
        args
    )
    worker.run()


if __name__ == '__main__':
    main()
