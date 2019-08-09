#!/usr/bin/env python3

import math

from deus import *
import fragility

def test_all_imports_are_ok():
    import scipy as sp
    import lxml.etree as le

def test_load_exposure_cell_iterable():
    filename = './testinputs/exposure.json'
    output = load_exposure_cell_iterable(filename)


def test_fragility_data_without_sublevel():
    data = {
        'meta': {
        },
        'data': [
            {
                'taxonomy': 'URM1',
                'D1_mean': 5.9,
                'D1_stddev': 0.8,
                'D2_mean': 6.7,
                'D2_stddev': 0.8,
                'imt': 'pga',
                'imu': 'g',
            },
            {
                'taxonomy': 'CM',
                'D1_mean': 7.6,
                'D1_stddev': 1.0,
                'D2_mean': 8.6,
                'D2_stddev': 1.0,
                'imt': 'pga',
                'imu': 'g',
            }
        ],
    }

    fg = fragility.FragilityData(data)

    taxonomy_data_urm1 = fg.get_data_for_taxonomy('URM1')

    assert taxonomy_data_urm1 is not None

    damage_states = [ds for ds in taxonomy_data_urm1]

    ds_1 = [ds for ds in damage_states if ds.to_damage_state == 'D1'][0]

    assert ds_1 is not None

    assert ds_1.from_damage_state == 'D0'

    p_0 = ds_1.get_probability_for_intensity(
        {'PGA': 0}, {'PGA': 'g'})

    assert math.fabs(p_0) < 0.0001

    p_1 = ds_1.get_probability_for_intensity(
        {'PGA': 1000}, {'PGA': 'g'})

    assert 0.896 < p_1 < 0.897


def test_fragility_data_with_sublevel():

    data = {
        'meta': {
        },
        'data': [
            {
                'taxonomy': 'URM1',
                'D_0_1_mean': 5.9,
                'D_0_1_stddev': 0.8,
                'D_0_2_mean': 6.7,
                'D_0_2_stddev': 0.8,
                'D_1_2_mean': 9.8,
                'D_1_2_stddev': 1.0,
                'imt': 'pga',
                'imu': 'g',
            },
            {
                'taxonomy': 'CM',
                'D_0_1_mean': 7.6,
                'D_0_1_stddev': 1.0,
                'D_0_2_mean': 8.6,
                'D_0_2_stddev': 1.0,
                'imt': 'pga',
                'imu': 'g',
            }
        ],
    }

    fg = fragility.FragilityData(data)

    taxonomy_data_urm1 = fg.get_data_for_taxonomy('URM1')

    assert taxonomy_data_urm1 is not None

    damage_states = [ds for ds in taxonomy_data_urm1]

    ds_1 = [ds for ds in damage_states if ds.to_damage_state == 'D1' and ds.from_damage_state=='D0'][0]

    assert ds_1 is not None

    ds_2 = [ds for ds in damage_states if ds.to_damage_state == 'D2' and ds.from_damage_state=='D1'][0]
    assert ds_2 is not None
    
