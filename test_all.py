#!/usr/bin/env python3

import math

import geopandas as gpd
import pandas as pd

from shapely import wkt

import exposure
import fragility


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

    frag = fragility.Fragility(data)
    fragprov = frag.to_fragility_provider()
    taxonomy_data_urm1 = fragprov.get_damage_states_for_taxonomy('URM1')

    assert taxonomy_data_urm1 is not None

    damage_states = [ds for ds in taxonomy_data_urm1]

    ds_1 = [ds for ds in damage_states if ds.to_state == 1][0]

    assert ds_1 is not None

    assert ds_1.from_state == 0

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

    frag = fragility.Fragility(data)
    fragprov = frag.to_fragility_provider()
    taxonomy_data_urm1 = fragprov.get_damage_states_for_taxonomy('URM1')

    assert taxonomy_data_urm1 is not None

    damage_states = [ds for ds in taxonomy_data_urm1]

    ds_1 = [
        ds for ds in damage_states if ds.to_state == 1 and ds.from_state == 0
    ][0]

    assert ds_1 is not None

    ds_2 = [
        ds for ds in damage_states if ds.to_state == 2 and ds.from_state == 1
    ][0]
    assert ds_2 is not None

    taxonomy_data_cm = fragprov.get_damage_states_for_taxonomy('CM')
    damage_states_cm = [ds for ds in taxonomy_data_cm]

    ds_1_2 = [
        ds for ds in damage_states_cm if ds.to_state == 2
        and ds.from_state == 1
    ][0]

    assert ds_1_2 is not None


def test_exposure_cell():
    data = pd.DataFrame({
        'geometry': ['POINT(12.0 15.0)'],
        'name': ['example point1'],
        'gc_id': ['abcdefg'],
        r'MCF\/DNO\/_1': [6],
        r'MUR+STDRE\/': [13],
    })
    geodata = gpd.GeoDataFrame(data)
    geodata['geometry'] = geodata['geometry'].apply(wkt.loads)
    series = geodata.iloc[0]

    exposure_cell = exposure.ExposureCell(series)

    lon, lat = exposure_cell.get_lon_lat_of_centroid()

    assert lon == 12.0
    assert lat == 15.0

    empty_exposure_cell = exposure_cell.new_prototype()

    lon2, lat2 = empty_exposure_cell.get_lon_lat_of_centroid()

    assert lon == lon2
    assert lat == lat2

    assert empty_exposure_cell._series['name'] == 'example point1'

    taxonomies = exposure_cell.get_taxonomies()

    assert exposure.Taxonomy(name=r'MCF\/DNO\/_1', count=6) in taxonomies


def test_exposure_taxonomy_damage_state():
    tax1 = exposure.Taxonomy(name=r'MCF\/DNO\/_1', count=6)

    ds1 = tax1.get_damage_state()

    assert ds1 == 0

    tax2 = exposure.Taxonomy(name=r'MCF\/DNO\/_1_D1', count=6)

    ds2 = tax2.get_damage_state()

    assert ds2 == 1

    tax3 = exposure.Taxonomy(name=r'MCF\/DNO\/_1_D5', count=6)

    ds3 = tax3.get_damage_state()

    assert ds3 == 5


def test_update_damage_state():
    updated = exposure.update_taxonomy_damage_state(r'MCF\/DNO\/_1', 0)
    assert updated == r'MCF\/DNO\/_1_D0'

    updated2 = exposure.update_taxonomy_damage_state(r'MCF\/DNO\/_1_D0', 1)
    assert updated2 == r'MCF\/DNO\/_1_D1'
