#!/bin/bash

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

python3 deus.py \
    --updated_exposure_output_file updated_exposure_output.json \
    --transition_output_file transition_output.json \
    --loss_output_file loss_output.json \
    testinputs/shakemap.xml \
    testinputs/exposure_from_assetmaster.json \
    'SARA_v1.0' \
    testinputs/fragility_sara.json
#python3 deus.py --updated_exposure_output_file updated_exposure_output_file_ts.json testinputs/shakemap_tsunami.xml testinputs/exposure_suppasri.json 'SARA_v1.0' testinputs/fragility_suppasri.json 
