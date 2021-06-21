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
Unit tests for all basic functions
"""

import unittest
import math
import os
import georasters as gr
import geopandas as gpd
import pandas as pd
from shapely import wkt

import gpdexposure
import intensitydatawrapper
import rasterwrapper
import fragility
import intensityprovider


class TestBasics(unittest.TestCase):
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
        schema = fragprov.schema

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

        ds_list.sort(key=gpdexposure.sort_by_to_damage_state_desc)

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


class MockedIntensityProvider:
    '''Just a dummy implementation.'''
    def get_nearest(self, lon, lat):
        '''Also a dummy implementation.'''
        return {'PGA': 1}, {'PGA': 'g'}


if __name__ == "__main__":
    unittest.main()
