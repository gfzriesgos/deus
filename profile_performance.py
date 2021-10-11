#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

import argparse
import cProfile
import glob
import os

import fragility
import gpdexposure
import intensityprovider
import loss
import shakemap
import tellus

gpdexposure.PARALLEL_PROCESSING = False

schema = 'SARA_v1.0'
current_dir = os.path.dirname(os.path.abspath(__file__))

testinput_dir = os.path.join(current_dir, 'testinputs', 'performance')
test_shakemap = os.path.join(testinput_dir, 'shakemap_ts.xml')
test_exposure_file = os.path.join(
    testinput_dir,
    'exposure_so_far.json'
)
test_fragility_file = os.path.join(
    testinput_dir,
    'fragility_suppasri.json'
)

output_dir = os.path.join(current_dir, 'testoutputs')

updated_exposure_output_filename = os.path.join(
    output_dir,
    'updated_exposure_ts_perf.json'
)
transition_output_filename = os.path.join(
    output_dir,
    'transitions_ts_perf.json'
)
loss_output_filename = os.path.join(output_dir, 'losses_ts_perf.json')
merged_output_filename = os.path.join(
    output_dir, 'merged_ts_perf.json'
)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

if os.path.exists(updated_exposure_output_filename):
    os.unlink(updated_exposure_output_filename)

if os.path.exists(transition_output_filename):
    os.unlink(transition_output_filename)

if os.path.exists(loss_output_filename):
    os.unlink(loss_output_filename)

if os.path.exists(merged_output_filename):
    os.unlink(merged_output_filename)

intensity_provider = shakemap.Shakemaps.from_file(
    test_shakemap).to_intensity_provider()
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
    test_fragility_file).to_fragility_provider()
old_exposure = gpdexposure.read_exposure(test_exposure_file)

current_dir = os.path.dirname(os.path.realpath(__file__))
loss_data_dir = os.path.join(current_dir, 'loss_data')
files = glob.glob(os.path.join(loss_data_dir, '*.json'))
loss_provider = loss.LossProvider.from_files(files, 'USD')

args = argparse.Namespace(
    updated_exposure_output_file=updated_exposure_output_filename,
    transition_output_file=transition_output_filename,
    loss_output_file=loss_output_filename,
    merged_output_file=merged_output_filename,
)

worker = tellus.Child(
    intensity_provider,
    fragility_provider,
    old_exposure,
    schema,
    loss_provider,
    args
)
cProfile.run('worker.run()')
