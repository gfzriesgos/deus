#!/usr/bin/env python3

"""
Unit tests for all basic functions
"""

import glob
import math
import os
import unittest

import geopandas as gpd
import georasters as gr
import pandas as pd

from shapely import wkt

import exposure
import fragility
import intensitydatawrapper
import intensityprovider
import rasterwrapper
import schemamapping
import shakemap

# import other test classes
from test_cmdexecution import *
from test_exposure import *
from test_fragility import *
from test_intensity import *
from test_loss import *
from test_schemamapping import *
from test_shakemap import *
from test_transition import *


class TestAll(unittest.TestCase):
    """
    Unit test class
    """

    def test_fragility_data_without_sublevel(self):
        """
        Test fragility data without sublevel
        :return: None
        """
        data = {
            'meta': {
                'shape': 'logncdf',
                'id': 'SARA_v1.0',
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
        schema = fragprov.get_schema()

        self.assertEqual('SARA_v1.0', schema)
        taxonomy_data_urm1 = fragprov.get_damage_states_for_taxonomy('URM1')

        self.assertIsNotNone(taxonomy_data_urm1)

        damage_states = [ds for ds in taxonomy_data_urm1]

        ds_1 = [ds for ds in damage_states if ds.to_state == 1][0]

        self.assertIsNotNone(ds_1)

        self.assertEqual(ds_1.from_state, 0)

        p_0 = ds_1.get_probability_for_intensity(
            {'PGA': 0}, {'PGA': 'g'})

        self.assertLess(math.fabs(p_0), 0.0001)

        p_1 = ds_1.get_probability_for_intensity(
            {'PGA': 1000}, {'PGA': 'g'})

        self.assertLess(0.896, p_1)
        self.assertLess(p_1, 0.897)

    def test_fragility_data_with_sublevel(self):
        """
        Test fragility data with sublevel
        :return: None
        """
        data = {
            'meta': {
                'shape': 'logncdf',
                'id': 'SARA_v1.0',
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

        self.assertIsNotNone(taxonomy_data_urm1)

        damage_states = [ds for ds in taxonomy_data_urm1]

        ds_1 = [
            ds for ds in damage_states if ds.to_state == 1
            and ds.from_state == 0
        ][0]

        self.assertIsNotNone(ds_1)

        ds_2 = [
            ds for ds in damage_states if ds.to_state == 2
            and ds.from_state == 1
        ][0]

        self.assertIsNotNone(ds_2)

        taxonomy_data_cm = fragprov.get_damage_states_for_taxonomy('CM')
        damage_states_cm = [ds for ds in taxonomy_data_cm]

        ds_1_2 = [
            ds for ds in damage_states_cm if ds.to_state == 2
            and ds.from_state == 1
        ][0]

        self.assertIsNotNone(ds_1_2)

    def test_exposure_cell(self):
        """
        Test exposure cell
        :return: None
        """
        exposure_cell = get_example_exposure_cell()

        lon, lat = exposure_cell.get_lon_lat_of_centroid()

        self.assertEqual(lon, 12.0)
        self.assertEqual(lat, 15.0)

        empty_exposure_cell = exposure_cell.without_taxonomies(
            schema='SARA_v1.0'
        )

        lon2, lat2 = empty_exposure_cell.get_lon_lat_of_centroid()

        self.assertEqual(lon, lon2)
        self.assertEqual(lat, lat2)

        self.assertEqual(
            empty_exposure_cell.get_name(),
            'example point1')

        taxonomies = exposure_cell.get_taxonomies()

        search_taxonomy = [
            x for x in taxonomies
            if x.get_schema() == 'SARA_v1.0'
            and x.get_taxonomy() == 'MCF/DNO/_1'
            and x.get_n_buildings() == 6
        ]

        self.assertEqual(1, len(search_taxonomy))

    def test_cell_mapping(self):
        '''
        Tests the schema mapping with a exposure
        cell.
        :return: None
        '''
        exposure_cell = get_exposure_cell_for_sara()

        schema_mapper = get_schema_mapper_for_sara_to_suppasri()

        mapped_exposure_cell = exposure_cell.map_schema(
            'SUPPASRI_2013.0', schema_mapper)

        new_schema = mapped_exposure_cell.get_schema()

        self.assertEqual('SUPPASRI_2013.0', new_schema)

        new_series = mapped_exposure_cell.to_simple_series()

        self.assertLess(79.9, new_series['RC_H1_D0'])
        self.assertLess(new_series['RC_H1_D0'], 80.1)

        self.assertLess(19.9, new_series['BRICK_D0'])
        self.assertLess(new_series['BRICK_D0'], 20.1)

        self.assertLess(49.9, new_series['MIX_D2'])
        self.assertLess(new_series['MIX_D2'], 50.1)

        self.assertLess(49.9, new_series['MIX_D3'])
        self.assertLess(new_series['MIX_D3'], 50.1)

        self.assertLess(49.9, new_series['STEEL_D2'])
        self.assertLess(new_series['STEEL_D2'], 50.1)

        self.assertLess(49.9, new_series['STEEL_D3'])
        self.assertLess(new_series['STEEL_D3'], 50.1)

    def test_cell_update(self):
        '''
        Tests the update of the damage states for
        a exposure cell.
        :return: None
        '''
        exposure_cell = get_exposure_cell_for_sara()

        fragility_data = {
            'meta': {
                'shape': 'logncdf',
                'id': 'SARA_v1.0',
            },
            'data': [
                {
                    'taxonomy': 'MUR_H1',
                    'D1_mean': -1.418,
                    'D1_stddev': 0.31,
                    'D2_mean': -0.709,
                    'D2_stddev': 0.328,
                    'D3_mean': -0.496,
                    'D3_stddev': 0.322,
                    'D4_mean': -0.231,
                    'D4_stddev': 0.317,
                    'imt': 'pga',
                    'imu': 'g',
                },
                {
                    'taxonomy': 'ER_ETR_H1_2',
                    'D1_mean': -1.418,
                    'D1_stddev': 0.31,
                    'D2_mean': -0.709,
                    'D2_stddev': 0.328,
                    'D3_mean': -0.496,
                    'D3_stddev': 0.317,
                    'D4_mean': -0.231,
                    'D4_stddev': 0.317,
                    'imt': 'pga',
                    'imu': 'g',
                }
            ],
        }

        fragility_provider = fragility.Fragility(
            fragility_data).to_fragility_provider()
        intensity_provider = MockedIntensityProvider()

        updated_exposure_cell, transition_cell = exposure_cell.update(
            intensity_provider, fragility_provider)

        self.assertEqual(
            updated_exposure_cell.get_schema(),
            exposure_cell.get_schema())

        updated_series = updated_exposure_cell.to_simple_series()

        self.assertLess(76.69, updated_series['MUR_H1_D4'])
        self.assertLess(updated_series['MUR_H1_D4'], 76.70)

        self.assertLess(21.87, updated_series['MUR_H1_D3'])
        self.assertLess(updated_series['MUR_H1_D3'], 21.88)

        self.assertLess(1.41, updated_series['MUR_H1_D2'])
        self.assertLess(updated_series['MUR_H1_D2'], 1.42)

        self.assertLess(0.022, updated_series['MUR_H1_D1'])
        self.assertLess(updated_series['MUR_H1_D1'], 0.023)

        self.assertLess(5.27e-8, updated_series['MUR_H1_D0'])
        self.assertLess(updated_series['MUR_H1_D0'], 5.28e-8)

        self.assertLess(153.38, updated_series['ER_ETR_H1_2_D4'])
        self.assertLess(updated_series['ER_ETR_H1_2_D4'], 153.39)

        self.assertLess(43.87, updated_series['ER_ETR_H1_2_D3'])
        self.assertLess(updated_series['ER_ETR_H1_2_D3'], 43.88)

        self.assertLess(2.74, updated_series['ER_ETR_H1_2_D2'])
        self.assertLess(updated_series['ER_ETR_H1_2_D2'], 2.75)

        transition_series = transition_cell.to_series()

        self.assertEqual(updated_series['gc_id'], transition_series['gid'])
        self.assertEqual(
            updated_series['geometry'],
            transition_series['geometry'])
        self.assertEqual(
            updated_series['name'],
            transition_series['name'])

        def filter_transitions(from_damage_state, to_damage_state, taxonomy):
            tst = transition_series['transitions']
            result = [
                tst['n_buildings'][i]
                for i in range(len(tst['taxonomy']))
                if tst['from_damage_state'][i] == from_damage_state
                and tst['to_damage_state'][i] == to_damage_state
                and tst['taxonomy'][i] == taxonomy][0]
            return result

        updates_mur_h1_0_1 = filter_transitions(0, 1, 'MUR_H1')
        self.assertLess(0.022, updates_mur_h1_0_1)
        self.assertLess(updates_mur_h1_0_1, 0.023)

        # the other mur updates are similar, not so fancy anyway

        updates_er_etr_h1_2_2_3 = filter_transitions(2, 3, 'ER_ETR_H1_2')
        self.assertLess(43.87, updates_er_etr_h1_2_2_3)
        self.assertLess(updates_er_etr_h1_2_2_3, 43.88)

        updates_er_etr_h1_2_2_4 = filter_transitions(2, 4, 'ER_ETR_H1_2')
        self.assertLess(153.38, updates_er_etr_h1_2_2_4)
        self.assertLess(updates_er_etr_h1_2_2_4, 153.39)

    def test_sorting_of_damage_states(self):
        '''
        Tests the sorting of damage states
        data according to their to state.
        :return: None
        '''
        ds1 = fragility.DamageState(
            taxonomy='xyz',
            from_state=1,
            to_state=2,
            intensity_field='xyz',
            intensity_unit='xyz',
            fragility_function=None)
        ds2 = fragility.DamageState(
            taxonomy='xyz',
            from_state=1,
            to_state=3,
            intensity_field='xyz',
            intensity_unit='xyz',
            fragility_function=None)

        ds_list = [ds1, ds2]

        ds_list.sort(key=exposure.sort_by_to_damage_state_desc)

        self.assertEqual(3, ds_list[0].to_state)
        self.assertEqual(2, ds_list[1].to_state)

    def test_intensity_provider(self):
        '''
        Tests a overall intensity provider.
        :return: None
        '''

        data = pd.DataFrame({
            'geometry': [
                'POINT(-71.5473 -32.8026)',
                'POINT(-71.5473 -32.8022)',
                'POINT(-71.5468 -32.803)',
                'POINT(-71.5467 -32.8027)',
            ],
            'value_mwh': [
                6.7135,
                7.4765,
                3.627,
                3.5967
            ],
            'unit_mwh': [
                'm',
                'm',
                'm',
                'm',
            ]
        })
        geodata = gpd.GeoDataFrame(data)
        geodata['geometry'] = geodata['geometry'].apply(wkt.loads)

        intensity_provider = intensityprovider.IntensityProvider(
            intensitydatawrapper.GeopandasDataFrameWrapper(geodata))

        intensities, units = intensity_provider.get_nearest(
            lon=-71.5473,
            lat=-32.8025
        )
        intensity_mwh = intensities['mwh']
        self.assertLess(6.7134, intensity_mwh)
        self.assertLess(intensity_mwh, 6.7136)

        self.assertEqual(units['mwh'], 'm')

    def test_raster(self):
        '''
        Test for reading from a raster directly.
        '''

        test_df = pd.DataFrame({
            'lon': [14, 15, 16, 14, 15, 16, 14, 15, 16],
            'lat': [50, 50, 50, 51, 51, 51, 52, 52, 52],
            'val': [11, 12, 13, 14, 15, 16, 17, 18, 19],
        })

        test_raster = gr.from_pandas(test_df, value='val', x='lon', y='lat')
        test_raster_wrapper = rasterwrapper.RasterWrapper(test_raster)

        intensity_provider = intensityprovider.RasterIntensityProvider(
            test_raster_wrapper,
            kind='testdata',
            unit='unitless',
        )

        intensities, units = intensity_provider.get_nearest(lon=15, lat=51)

        intensity_testdata = intensities['testdata']
        self.assertLess(14.9, intensity_testdata)
        self.assertLess(intensity_testdata, 15.1)

        units_testdata = units['testdata']
        self.assertEqual(units_testdata, 'unitless')

        intensities2, units2 = intensity_provider.get_nearest(lon=13, lat=50)

        self.assertEqual(intensities2['testdata'], 0.0)
        self.assertEqual(units2['testdata'], 'unitless')

    def test_read_lahar_data(self):
        '''
        Test the intensity provider of the lahar data.
        '''
        current_dir = os.path.dirname(os.path.realpath(__file__))
        raster = gr.from_file(os.path.join(
            current_dir,
            'testinputs',
            'fixedDEM_S_VEI_60mio_HYDRO_v10_EROSION_1600_0015_' +
            '25res_4mom_25000s_MaxPressure_smaller.asc'
        ))

        intensity_data = intensitydatawrapper.RasterDataWrapper(
            raster=raster,
            value_name='max_pressure',
            # check the unit; for testing it is ok to assume that it is p
            unit='p',
            input_epsg_code='epsg:24877',
            usage_epsg_code='epsg:4326'
        )

        intensity_provider = intensityprovider.IntensityProvider(
            intensity_data
        )

        intensities, units = intensity_provider.get_nearest(
            lon=-78.48187327247078,
            lat=-0.7442986459402828,
        )

        intensity_max_pressure = intensities['max_pressure']

        self.assertLess(11156.0, intensity_max_pressure)
        self.assertLess(intensity_max_pressure, 11156.2)

        self.assertEqual('p', units['max_pressure'])

    def test_stacked_intensity_provider(self):
        '''
        Tests the stacked intensity provider.
        :return: None
        '''
        data1 = pd.DataFrame({
            'geometry': [
                'POINT(-71.5473 -32.8026)',
                'POINT(-71.5473 -32.8022)',
                'POINT(-71.5468 -32.803)',
                'POINT(-71.5467 -32.8027)',
            ],
            'value_mwh': [
                6.7135,
                7.4765,
                3.627,
                3.5967
            ],
            'unit_mwh': [
                'm',
                'm',
                'm',
                'm',
            ]
        })
        geodata1 = gpd.GeoDataFrame(data1)
        geodata1['geometry'] = geodata1['geometry'].apply(wkt.loads)

        intensity_provider1 = intensityprovider.IntensityProvider(
            intensitydatawrapper.GeopandasDataFrameWrapper(geodata1))

        data2 = pd.DataFrame({
            'geometry': [
                'POINT(-71.5473 -32.8026)',
                'POINT(-71.5473 -32.8022)',
                'POINT(-71.5468 -32.803)',
                'POINT(-71.5467 -32.8027)',
            ],
            'value_pga': [
                0.7135,
                0.4765,
                0.627,
                0.5967
            ],
            'unit_pga': [
                'g',
                'g',
                'g',
                'g',
            ]
        })
        geodata2 = gpd.GeoDataFrame(data2)
        geodata2['geometry'] = geodata2['geometry'].apply(wkt.loads)

        intensity_provider2 = intensityprovider.IntensityProvider(
            intensitydatawrapper.GeopandasDataFrameWrapper(geodata2))

        stacked_intensity_provider = \
            intensityprovider.StackedIntensityProvider(
                intensity_provider1,
                intensity_provider2
            )

        intensities, units = stacked_intensity_provider.get_nearest(
            lon=-71.5473,
            lat=-32.8025
        )
        intensity_mwh = intensities['mwh']
        self.assertLess(6.7134, intensity_mwh)
        self.assertLess(intensity_mwh, 6.7136)
        intensity_pga = intensities['pga']
        self.assertLess(0.7134, intensity_pga)
        self.assertLess(intensity_pga, 0.7136)
        self.assertEqual(units['mwh'], 'm')
        self.assertEqual(units['pga'], 'g')


class MockedIntensityProvider():
    '''Just a dummy implementation.'''
    def get_nearest(self, lon, lat):
        '''Also a dummy implementation.'''
        return {'PGA': 1}, {'PGA': 'g'}


def get_example_exposure_cell():
    '''
    Returns an example exposure cell.
    :return: None
    '''
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
    return exposure.ExposureCell.from_simple_series(
        series=series,
        schema='SARA_v1.0'
    )


def get_exposure_cell_for_sara():
    '''
    Returns an example cell with sara
    schema.
    '''

    exposure_cell_data = gpd.GeoDataFrame(pd.DataFrame({
        'geometry': ['POINT(12.0 15.0)'],
        'name': ['example point1'],
        'gc_id': ['abcdefg'],
        'MUR_H1': [100.0],
        'ER_ETR_H1_2_D2': [200.0]
    }))
    exposure_cell_data['geometry'] = exposure_cell_data['geometry'].apply(
        wkt.loads)
    exposure_cell_series = exposure_cell_data.iloc[0]

    return exposure.ExposureCell.from_simple_series(
        series=exposure_cell_series,
        schema='SARA_v1.0'
    )


def get_schema_mapper_for_sara_to_suppasri():
    '''
    Returns the mapper from sara to suppasri.
    '''
    bc_mapping_data = [
        {
            'source_schema': 'SARA_v1.0',
            'target_schema': 'SUPPASRI_2013.0',
            'conv_matrix': {
                'MUR_H1': {
                    'RC_H1': 0.8,
                    'BRICK': 0.2,
                },
                'ER_ETR_H1_2': {
                    'MIX': 0.5,
                    'STEEL': 0.5,
                },
            }
        },
    ]

    building_class_mapper = schemamapping.BuildingClassMapper(bc_mapping_data)

    ds_mapping_data = [
        {
            'source_schema': 'SARA_v1.0',
            'target_schema': 'SUPPASRI_2013.0',
            'conv_matrix': {
                '0': {
                    '0': 1.0,
                },
                '1': {
                    '1': 1.0,
                },
                '2': {
                    '2': 0.5,
                    '3': 0.5,
                },
                '3': {
                    '4': 0.5,
                    '5': 0.5,
                },
                '4': {
                    '6': 1.0,
                },
            },
        },
    ]

    damage_state_mapper = schemamapping.DamageStateMapper(ds_mapping_data)

    return schemamapping.SchemaMapper(
        building_class_mapper, damage_state_mapper)


if __name__ == "__main__":
    unittest.main()
