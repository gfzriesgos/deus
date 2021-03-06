#!/bin/bash

python3 deus.py \
    --updated_exposure_output_file updated_exposure_output.json \
    --transition_output_file transition_output.json \
    --loss_output_file loss_output.json \
    testinputs/shakemap.xml \
    testinputs/exposure_from_assetmaster.json \
    'SARA_v1.0' \
    testinputs/fragility_sara.json
#python3 deus.py --updated_exposure_output_file updated_exposure_output_file_ts.json testinputs/shakemap_tsunami.xml testinputs/exposure_suppasri.json 'SARA_v1.0' testinputs/fragility_suppasri.json 
