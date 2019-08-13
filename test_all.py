#!/usr/bin/env python3

"""
Unit tests for all basic functions
"""

import math
import unittest

import geopandas as gpd
import pandas as pd

from shapely import wkt

import exposure
import fragility


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

        self.assertEqual(lon, 12.0)
        self.assertEqual(lat, 15.0)

        empty_exposure_cell = exposure_cell.new_prototype()

        lon2, lat2 = empty_exposure_cell.get_lon_lat_of_centroid()

        self.assertEqual(lon, lon2)
        self.assertEqual(lat, lat2)

        self.assertEqual(empty_exposure_cell._series['name'], 'example point1')

        taxonomies = exposure_cell.get_taxonomies()

        self.assertIn(
            exposure.Taxonomy(name=r'MCF\/DNO\/_1', count=6),
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


if __name__ == "__main__":
    unittest.main()
