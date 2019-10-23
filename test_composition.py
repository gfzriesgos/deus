#!/usr/bin/env python3

"""
This is the test module
for the composition of
several classes.

For example: The work of
exposure cells, schema mappings and
fragility functions.
"""

import unittest

import pandas as pd
from shapely import wkt

import exposure
import fragility
import schemamapping

import testimplementations

class TestComposition(unittest.TestCase):
    """
    The test class for all tests
    of the composition of classes in deus.
    """

    def test_update_exposure_cell_with_missing_d1(self):
        """
        Here we have a test case in which we
        have an exposure model (all D0), update
        it with an intensity and fragility functions.
        
        But we only have fragility functions for D0, D2 and D3,
        but none for D1.

        As there is simply no D1 in the given exposure model,
        it should just work as expected.
        """

        schema = 'SARA_v1.0'
        taxonomy = 'MUR-H1'

        geometry = wkt.loads('POINT(14 51)')

        dataframe = pd.DataFrame({
            'name': ['Colina'],
            'gc_id': ['CHL.14.1.1_1'],
            'geometry': [geometry],
            taxonomy : [100.0]
        })

        exposure_cell_list = exposure.ExposureCellList.from_simple_dataframe(
            schema=schema,
            dataframe=dataframe
        )
        
        exposure_cell = exposure_cell_list.get_exposure_cells()[0]

        fragility_data = {
            'meta': {
                'id': schema,
                'shape': 'logncdf',
            },
            'data': [
                {
                    'taxonomy': taxonomy,
                    'D2_mean': -0.709,
                    'D2_stddev': 0.328,
                    'D3_mean': -0.496,
                    'D3_stddev': 0.322,
                    'imt': 'PGA',
                    'imu': 'g',
                }
            ]
        }

        fragility_instance = fragility.Fragility(fragility_data)
        fragility_provider = fragility_instance.to_fragility_provider()

        intensity_provider = testimplementations.AlwaysTheSameIntensityProvider(
            kind='PGA',
            value=1.0,
            unit='g',
        )

        updated_cell, transition_cell = exposure_cell.update(intensity_provider, fragility_provider)

        for taxonomy_bag in updated_cell.get_taxonomies():
            ds = taxonomy_bag.get_damage_state()
            # we can't have D1 here
            self.assertNotEqual(1, ds)
            n_buildings = taxonomy_bag.get_n_buildings()
            # the most buildings will be in damage state 3
            # some (~ 4) in damage state 2
            # and below 1 remain in damage state 0
            self.assertLess(0, n_buildings)

        # ok we have no problem with 
        # it if we don't get any damage state 1
        # as input

    def test_update_exposure_cell_with_missing_d1_but_with_d1_in_exposure(self):
        """
        This is mostly the very same test as
        test_update_exposure_cell_with_missing_d1, but it now contains
        D1 in the exposure model (instead of D0).

        It should just take D1 as input with some remaining buildings,
        but since there is no fragility model for them no new building
        will be inserted into D1.
        """

        schema = 'SARA_v1.0'
        taxonomy = 'MUR-H1'
        taxonomy_d1 = taxonomy + '_D1'

        geometry = wkt.loads('POINT(14 51)')

        dataframe = pd.DataFrame({
            'name': ['Colina'],
            'gc_id': ['CHL.14.1.1_1'],
            'geometry': [geometry],
            taxonomy_d1 : [100.0]
        })

        exposure_cell_list = exposure.ExposureCellList.from_simple_dataframe(
            schema=schema,
            dataframe=dataframe
        )
        
        exposure_cell = exposure_cell_list.get_exposure_cells()[0]

        fragility_data = {
            'meta': {
                'id': schema,
                'shape': 'logncdf',
            },
            'data': [
                {
                    'taxonomy': taxonomy,
                    'D2_mean': -0.709,
                    'D2_stddev': 0.328,
                    'D3_mean': -0.496,
                    'D3_stddev': 0.322,
                    'imt': 'PGA',
                    'imu': 'g',
                }
            ]
        }

        fragility_instance = fragility.Fragility(fragility_data)
        fragility_provider = fragility_instance.to_fragility_provider()

        intensity_provider = testimplementations.AlwaysTheSameIntensityProvider(
            kind='PGA',
            value=1.0,
            unit='g',
        )

        updated_cell, transition_cell = exposure_cell.update(intensity_provider, fragility_provider)

        # this is the very same result as in the last test
        # but this time the data remains in D1 instead of D0


        for taxonomy_bag in updated_cell.get_taxonomies():
            ds = taxonomy_bag.get_damage_state()
            # we can't have D1 here
            self.assertNotEqual(0, ds)
            self.assertIn(ds, [1, 2, 3])
            n_buildings = taxonomy_bag.get_n_buildings()
            # the most buildings will be in damage state 3
            # some (~ 4) in damage state 2
            # and below 1 remain in damage state 1
            self.assertLess(0, n_buildings)

        # again we have no problem with it
        # as we just stay with some D1 buildings in our model


if __name__ == '__main__':
    unittest.main()
