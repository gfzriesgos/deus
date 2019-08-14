#!/usr/bin/env python3

"""
Unit tests for all basic functions
"""

import glob
import math
import os
import unittest

import geopandas as gpd
import pandas as pd

from shapely import wkt

import exposure
import fragility
from taxonomymapping import DamageStateMapper
from deus import update_exposure_cell


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
        exposure_cell = TestAll._get_example_exposure_cell()

        lon, lat = exposure_cell.get_lon_lat_of_centroid()

        self.assertEqual(lon, 12.0)
        self.assertEqual(lat, 15.0)

        empty_exposure_cell = exposure_cell.new_prototype()

        lon2, lat2 = empty_exposure_cell.get_lon_lat_of_centroid()

        self.assertEqual(lon, lon2)
        self.assertEqual(lat, lat2)

        self.assertEqual(
            empty_exposure_cell.get_series()['name'],
            'example point1')

        taxonomies = exposure_cell.get_taxonomies()

        self.assertIn(
            # the backslashes are removed
            exposure.Taxonomy(name=r'MCF/DNO/_1', count=6),
            taxonomies
        )

    def test_exposure_taxonomy_damage_state(self):
        """
        Test exposure taxonomy damage state
        :return: None
        """
        tax1 = exposure.Taxonomy(name=r'MCF\/DNO\/_1', count=6)

        ds1 = tax1.get_damage_state()

        self.assertEqual(ds1, 0)

        tax2 = exposure.Taxonomy(name=r'MCF\/DNO\/_1_D1', count=6)

        ds2 = tax2.get_damage_state()

        self.assertEqual(ds2, 1)

        tax3 = exposure.Taxonomy(name=r'MCF\/DNO\/_1_D5', count=6)

        ds3 = tax3.get_damage_state()

        self.assertEqual(ds3, 5)

    def test_update_damage_state(self):
        """
        Test update damage state
        :return: None
        """
        updated = exposure.update_taxonomy_damage_state(r'MCF\/DNO\/_1', 0)
        self.assertEqual(updated, r'MCF\/DNO\/_1_D0')

        updated2 = exposure.update_taxonomy_damage_state(r'MCF\/DNO\/_1_D0', 1)
        self.assertEqual(updated2, r'MCF\/DNO\/_1_D1')

    @staticmethod
    def _get_example_exposure_cell():
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
        return exposure.ExposureCell(series)

    def test_update_exposure_cell(self):
        '''
        Test the update of one exposure cell.
        :return: None
        '''

        exposure_cell = TestAll._get_example_exposure_cell()

        fragility_data = {
            'meta': {
                'shape': 'logncdf',
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
            ],
        }

        frag = fragility.Fragility(fragility_data)
        fragprov = frag.to_fragility_provider()

        class MockedIntensityProvider():
            '''Just a dummy implementation.'''
            def get_nearest(self, lon, lat):
                '''Also a dummy implementation.'''
                return {'PGA': 100}, {'PGA': 'g'}

        intensity_provider = MockedIntensityProvider()

        class MockedTaxonomyMapper():
            '''Dummy implementation.'''
            def find_fragility_taxonomy_and_new_exposure_taxonomy(
                    self,
                    exposure_taxonomy,
                    actual_damage_state,
                    fragility_taxonomies):
                '''Dummy implementation.'''
                return 'URM1', exposure_taxonomy, actual_damage_state
        taxonomy_mapper = MockedTaxonomyMapper()

        updated_exposure_cell = update_exposure_cell(
            exposure_cell,
            intensity_provider,
            fragprov,
            taxonomy_mapper)

        self.assertIsNotNone(update_exposure_cell)

        series = updated_exposure_cell.get_series()

        # we don't have anymore 6 buildings in damage state 0
        self.assertIn('MCF/DNO/_1_D0', series.keys())
        buildings_d0 = series['MCF/DNO/_1_D0']
        self.assertLess(buildings_d0, 5.7)
        self.assertLess(5.6, buildings_d0)

        # a small amount in damage state 1
        self.assertIn('MCF/DNO/_1_D1', series.keys())
        buildings_d1 = series['MCF/DNO/_1_D1']
        self.assertLess(buildings_d1, 0.32)
        self.assertLess(0.31, buildings_d1)

        # and an even smaller amount in damage state 2
        self.assertIn('MCF/DNO/_1_D2', series.keys())
        buildings_d2 = series['MCF/DNO/_1_D2']
        self.assertLess(buildings_d2, 0.03)
        self.assertLess(0.02, buildings_d2)

        # all togehter are still the overall 6 buildings
        buildings_all = buildings_d0 + buildings_d1 + buildings_d2
        self.assertLess(buildings_all, 6.0001)
        self.assertLess(5.9999, buildings_all)

        # and we can run the update procedure again

        again_updated_exposure_cell = update_exposure_cell(
            updated_exposure_cell,
            intensity_provider,
            fragprov,
            taxonomy_mapper)

        series_again_updated = again_updated_exposure_cell.get_series()

        buildings_again_updated_d0 = series_again_updated['MCF/DNO/_1_D0']
        buildings_again_updated_d1 = series_again_updated['MCF/DNO/_1_D1']
        buildings_again_updated_d2 = series_again_updated['MCF/DNO/_1_D2']

        # as we run the same event again
        # there should be less buildings in damage state 0
        self.assertLess(buildings_again_updated_d0, buildings_d0)
        # it depends on the fragility functions
        # if we have more in damage state 1 (as they were not damaged
        # in the first run) or less (as most of the damage state 1 buildings
        # are now even stronger damaged, so that they are in damage state 2)
        # however as damage state 2 is our highest damage state here
        # we will have more buildings in this state
        self.assertLess(buildings_d2, buildings_again_updated_d2)
        # and all of the damage state buildings should are around the
        # overall count of buildings here too
        buildings_again_updated_all = buildings_again_updated_d0 + \
            buildings_again_updated_d1 + \
            buildings_again_updated_d2

        self.assertLess(buildings_again_updated_all, 6.0001)
        self.assertLess(5.9999, buildings_again_updated_all)

    def test_damage_state_mapping(self):
        '''
        Test the mapping of one damage state to another.
        :return: None
        '''

        mapping_data = [
            {
                'source_name': 'sup_13',
                'target_name': 'ems_98',
                'conv_matrix': {
                    '0': {
                        '0': 1,
                    },
                    '1': {
                        '1': 1,
                    },
                    '2': {
                        '2': 1,
                    },
                    '3': {
                        '3': 1,
                    },
                    '4': {
                        '4': 1,
                    },
                    '5': {
                        '5': 1,
                    },
                    '6': {
                        '5': 1
                    },
                },
            },
            {
                'source_name': 'ems_98',
                'target_name': 'sup_13',
                'conv_matrix': {
                    '0': {
                        '0': 1,
                    },
                    '1': {
                        '1': 1,
                    },
                    '2': {
                        '2': 1,
                    },
                    '3': {
                        '3': 1,
                    },
                    '4': {
                        '4': 1,
                    },
                    '5': {
                        '5': 0.5,
                        '6': 0.5,
                    },
                },
            },
        ]
        damage_state_mapper = DamageStateMapper(mapping_data)

        result_0_sup_to_sup = damage_state_mapper.map_damage_state(
            source_damage_state=0,
            source_name='sup_13',
            target_name='sup_13',
            n_buildings=100.0
        )

        self.assertEqual(1, len(result_0_sup_to_sup))
        self.assertEqual(0, result_0_sup_to_sup[0].get_damage_state())
        self.assertLess(99.9999, result_0_sup_to_sup[0].get_n_buildings())
        self.assertLess(result_0_sup_to_sup[0].get_n_buildings(), 100.0001)

        result_0_sup_to_ems = damage_state_mapper.map_damage_state(
            source_damage_state=0,
            source_name='sup_13',
            target_name='ems_98',
            n_buildings=100.0
        )

        self.assertEqual(1, len(result_0_sup_to_ems))
        self.assertEqual(0, result_0_sup_to_ems[0].get_damage_state())
        self.assertLess(99.9999, result_0_sup_to_ems[0].get_n_buildings())
        self.assertLess(result_0_sup_to_ems[0].get_n_buildings(), 100.0001)

        result_5_ems_to_sup = damage_state_mapper.map_damage_state(
            source_damage_state=5,
            source_name='ems_98',
            target_name='sup_13',
            n_buildings=100.0
        )
        self.assertEqual(2, len(result_5_ems_to_sup))
        result_5_ems_to_sup_to_5 = [
            x for x in result_5_ems_to_sup
            if x.get_damage_state() == 5][0]
        result_5_ems_to_sup_to_6 = [
            x for x in result_5_ems_to_sup
            if x.get_damage_state() == 6][0]

        self.assertLess(49.999, result_5_ems_to_sup_to_5.get_n_buildings())
        self.assertLess(result_5_ems_to_sup_to_5.get_n_buildings(), 50.001)

        self.assertLess(49.999, result_5_ems_to_sup_to_6.get_n_buildings())
        self.assertLess(result_5_ems_to_sup_to_6.get_n_buildings(), 50.001)

    def test_load_damage_state_conversions_from_files(self):
        '''
        Test the read process of the damage states.
        :return: None
        '''
        current_dir_with_test_in = os.path.dirname(
            os.path.realpath(__file__))
        pattern_to_search = os.path.join(
            current_dir_with_test_in, 'mapping*.json')
        files = glob.glob(pattern_to_search)

        damage_state_mapper = DamageStateMapper.from_files(files)
        self.assertIsNotNone(damage_state_mapper)


if __name__ == "__main__":
    unittest.main()
