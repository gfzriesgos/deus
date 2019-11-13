#!/usr/bin/env python3

'''
Test classes for the exposure.
'''

import unittest

import pandas as pd
from shapely import wkt

import exposure


class TestExposure(unittest.TestCase):
    '''
    Testclass for the exposur.
    '''

    def test_exposure_cell_list_from_simple_dataframe(self):
        '''
        Tests the conversion from an exposure cell list
        to a dataframe (simple - "old" - format).
        '''
        geometry1 = wkt.loads('POINT(14 51)')
        geometry2 = wkt.loads('POINT(15 52)')

        dataframe = pd.DataFrame({
            'name': ['Colina', 'Quilpue'],
            'gc_id': ['CHL.14.1.1_1', 'CHL.14.2.1-1'],
            'geometry': [geometry1, geometry2],
            'W+WS/H:1,2': [100.0, 80.0],
            'W+WS/H:1,2_D1': [50.0, 55.0]
        })
        schema = 'SARA_v1.0'
        exposure_cell_list = exposure.ExposureCellList.from_simple_dataframe(
            schema=schema,
            dataframe=dataframe
        )

        self.assertEqual(2, len(exposure_cell_list.exposure_cells))

        recreated_dataframe = exposure_cell_list.to_simple_dataframe()

        self.assertTrue(all(
            dataframe['geometry'] == recreated_dataframe['geometry']
        ))
        self.assertTrue(all(
            dataframe['name'] == recreated_dataframe['name']
        ))
        self.assertTrue(all(
            dataframe['gc_id'] == recreated_dataframe['gc_id']
        ))

        self.assertTrue(all(
            dataframe['W+WS/H:1,2'] == recreated_dataframe['W+WS/H:1,2_D0']
        ))
        self.assertTrue(all(
            dataframe['W+WS/H:1,2_D1'] == recreated_dataframe['W+WS/H:1,2_D1']
        ))

    def test_exposure_cell_list_from_dataframe(self):
        '''
        Tests the conversion from an exposure cell list
        to a dataframe (more complex).
        '''
        geometry1 = wkt.loads('POINT(14 51)')
        geometry2 = wkt.loads('POINT(15 52)')

        dataframe = pd.DataFrame({
            'name': ['Colina', 'Quilpue'],
            'gid': ['CHL.14.1.1_1', 'CHL.14.2.1-1'],
            'geometry': [geometry1, geometry2],
            'expo': [
                {
                    'id': ['AREA # 13301', 'AREA # 13301'],
                    'Region': ['Colina', 'Colina'],
                    'Taxonomy': ['W+WS/H:1,2', 'W+WS/H:1,2'],
                    'Dwellings': [107.5, 107.5],
                    'Buildings': [100.0, 50.0],
                    'Repl-cost-USD-bdg': [360000, 450000],
                    'Population': [446.5, 446.5],
                    'name': ['Colina', 'Colina'],
                    'Damage': ['D0', 'D1']
                },
                {
                    'id': ['AREA # 13302', 'AREA # 13302'],
                    'Region': ['Quilpue', 'Quilpue'],
                    'Taxonomy': ['W+WS/H:1,2', 'W+WS/H:1,2'],
                    'Dwellings': [107.5, 107.5],
                    'Buildings': [80.0, 55.0],
                    'Repl-cost-USD-bdg': [360000, 450000],
                    'Population': [446.5, 446.5],
                    'name': ['Quilpue', 'Quilpue'],
                    'Damage': ['D0', 'D1']
                }
            ]
        })
        schema = 'SARA_v1.0'
        exposure_cell_list = exposure.ExposureCellList.from_dataframe(
            schema=schema,
            dataframe=dataframe
        )

        self.assertEqual(2, len(exposure_cell_list.exposure_cells))

        recreated_dataframe = exposure_cell_list.to_dataframe()

        self.assertTrue(all(
            dataframe['geometry'] == recreated_dataframe['geometry']
        ))
        self.assertTrue(all(
            dataframe['name'] == recreated_dataframe['name']
        ))
        self.assertTrue(all(
            dataframe['gid'] == recreated_dataframe['gid']
        ))
        self.assertTrue(all(
            dataframe['expo'] == recreated_dataframe['expo']
        ))

    def test_exposure_cell_list(self):
        '''
        Tests the exposure cell list.
        '''
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = exposure.ExposureCell.from_simple_series(
            schema=schema,
            series=series1
        )

        geometry2 = wkt.loads('POINT(15 52)')
        series2 = pd.Series({
            'name': 'Quilpue',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry2,
            'W+WS/H:1,2': 80.0,
            'W+WS/H:1.2_D1': 30.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell2 = exposure.ExposureCell.from_simple_series(
            schema=schema,
            series=series2
        )

        exposure_cell_list = exposure.ExposureCellList(
            exposure_cells=[exposure_cell1, exposure_cell2]
        )

        self.assertEqual(2, len(exposure_cell_list.exposure_cells))

    def test_exposure_cell_from_simple_series(self):
        '''
        Tests the conversion from an exposure cell list
        to a series (with columns for the taxonomy + damage states
        and the values of this columns for the number of buildings).
        '''
        geometry = wkt.loads('POINT(14 51)')
        series = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell = exposure.ExposureCell.from_simple_series(
            schema=schema,
            series=series
        )

        self.assertEqual('SARA_v1.0', exposure_cell.schema)
        self.assertEqual('CHL.14.1.1_1', exposure_cell.gid)
        self.assertEqual('Colina', exposure_cell.name)
        self.assertEqual(geometry, exposure_cell.geometry)
        lon, lat = exposure_cell.get_lon_lat_of_centroid()
        self.assertEqual(14, lon)
        self.assertEqual(51, lat)
        self.assertEqual(2, len(exposure_cell.taxonomies))
        first_tax = exposure_cell.taxonomies[0]
        self.assertEqual(0, first_tax.damage_state)
        second_tax = exposure_cell.taxonomies[1]
        self.assertEqual(1, second_tax.damage_state)

    def test_exposure_cell_from_series(self):
        '''
        Tests the conversion from an exposure cell list
        to a series.
        '''
        geometry = wkt.loads('POINT(14 51)')
        series = pd.Series({
            'name': 'Colina',
            'gid': 'CHL.14.1.1_1',
            'geometry': geometry,
            'expo': {
                'id': ['AREA # 13301', 'AREA # 13301'],
                'Region': ['Colina', 'Colina'],
                'Taxonomy': ['W+WS/H:1,2', 'W+WS/H:1,2'],
                'Dwellings': [107.5, 107.5],
                'Buildings': [100.0, 50.0],
                'Repl-cost-USD-bdg': [360000, 450000],
                'Population': [446.5, 446.5],
                'name': ['Colina', 'Colina'],
                'Damage': ['D0', 'D1']
            }
        })

        schema = 'SARA_v1.0'
        exposure_cell = exposure.ExposureCell.from_series(schema, series)

        self.assertEqual('SARA_v1.0', exposure_cell.schema)
        self.assertEqual('CHL.14.1.1_1', exposure_cell.gid)
        self.assertEqual('Colina', exposure_cell.name)
        self.assertEqual(geometry, exposure_cell.geometry)
        lon, lat = exposure_cell.get_lon_lat_of_centroid()
        self.assertEqual(14, lon)
        self.assertEqual(51, lat)
        self.assertEqual(2, len(exposure_cell.taxonomies))
        first_tax = exposure_cell.taxonomies[0]
        self.assertEqual(0, first_tax.damage_state)
        second_tax = exposure_cell.taxonomies[1]
        self.assertEqual(1, second_tax.damage_state)

    def test_exposure_cell(self):
        '''
        Test of an exposure cell.
        '''
        tdb1 = exposure.TaxonomyDataBag(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            damage_state=0,
            n_buildings=100.0,
            area_id='AREA # 13301',
            region='Colina',
            dwellings=107.5,
            repl_cost_usd_bdg=360000,
            population=446.5,
            name='Colina'
        )
        tdb2 = exposure.TaxonomyDataBag(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            damage_state=1,
            n_buildings=50.0,
            area_id='AREA # 13301',
            region='Colina',
            dwellings=107.5,
            repl_cost_usd_bdg=360000,
            population=446.5,
            name='Colina'
        )
        geometry = wkt.loads('POINT(14 51)')
        exposure_cell = exposure.ExposureCell(
            schema='SARA_v1.0',
            gid='CHL.14.1.1_1',
            name='Colina',
            geometry=geometry,
            taxonomies=[tdb1, tdb2]
        )

        self.assertEqual('SARA_v1.0', exposure_cell.schema)
        self.assertEqual('CHL.14.1.1_1', exposure_cell.gid)
        self.assertEqual('Colina', exposure_cell.name)
        self.assertEqual(geometry, exposure_cell.geometry)
        lon, lat = exposure_cell.get_lon_lat_of_centroid()
        self.assertEqual(14, lon)
        self.assertEqual(51, lat)
        self.assertEqual(2, len(exposure_cell.taxonomies))

    def test_extract_damage_state_from_taxonomy_damage_state_string(self):
        '''
        Test to extract the damage state from a string with
        taxonomy and damage state.
        '''
        self.assertEqual(
            0, exposure.extract_damage_state_from_taxonomy_damage_state_string(
                'W+WS/H:1,2'
            )
        )
        self.assertEqual(
            2,
            exposure.extract_damage_state_from_taxonomy_damage_state_string(
                'W+WS/H:1,2_D2'
            )
        )

    def test_extract_taxonomy_from_taxonomy_damage_state_string(self):
        '''
        Test to extract the taxonomy from a string with
        taxonomy and damage state.
        '''
        self.assertEqual(
            'W+WS/H:1,2',
            exposure.extract_taxonomy_from_taxonomy_damage_state_string(
                'W+WS/H:1,2'
            )
        )
        self.assertEqual(
            'W+WS/H:1,2',
            exposure.extract_taxonomy_from_taxonomy_damage_state_string(
                'W+WS/H:1,2_D2'
            )
        )

    def test_taxonomy_data_bag_from_simple_series(self):
        '''
        Test to read the taxonomy data from a simple
        series.
        '''
        series = pd.Series({
            'W+WS/H:1,2_D3': 100.0,
            'name': 'Colina',
            'gid': 'xyz123',
            # won't be used here
            'geometry': 'POINT(1 1)',
        })

        schema = 'SARA_v1.0'
        tdb = exposure.TaxonomyDataBag.from_simple_series(
            series=series,
            key='W+WS/H:1,2_D3',
            schema=schema
        )

        self.assertEqual('SARA_v1.0', tdb.schema)
        self.assertEqual('W+WS/H:1,2', tdb.taxonomy)
        self.assertEqual(3, tdb.damage_state)
        self.assertEqual(100.0, tdb.n_buildings)
        self.assertEqual('Colina', tdb.name)

    def test_remove_prefix_d_for_damage_state(self):
        '''
        Test to remove the prefix d of the damage state strings.
        '''
        self.assertEqual(0, exposure.remove_prefix_d_for_damage_state('D0'))
        self.assertEqual(1, exposure.remove_prefix_d_for_damage_state('D1'))
        self.assertEqual(10, exposure.remove_prefix_d_for_damage_state('D10'))

    def test_taxonomy_data_bag_from_series(self):
        '''
        Test to create a taxonomy data bag from a
        series.
        '''
        series = pd.Series({
            'id': 'AREA # 13301',
            'Region': 'Colina',
            'Taxonomy': 'W+WS/H:1,2',
            'Dwellings': 107.5,
            'Buildings': 100.0,
            'Repl-cost-USD-bdg': 360000,
            'Population': 446.5,
            'name': 'Colina',
            'Damage': 'D0'
        })

        schema = 'SARA_v1.0'

        tdb = exposure.TaxonomyDataBag.from_series(
            series, schema
        )

        self.assertEqual('SARA_v1.0', tdb.schema)
        self.assertEqual('W+WS/H:1,2', tdb.taxonomy)
        self.assertEqual(0, tdb.damage_state)
        self.assertEqual(100.0, tdb.n_buildings)
        self.assertEqual('AREA # 13301', tdb.area_id)
        self.assertEqual('Colina', tdb.region)
        self.assertLess(107.4, tdb.dwellings)
        self.assertLess(tdb.dwellings, 107.6)
        self.assertEqual(360000, tdb.repl_cost_usd_bdg)
        self.assertLess(446.4, tdb.population)
        self.assertLess(tdb.population, 446.6)
        self.assertEqual('Colina', tdb.name)

    def test_taxonomy_data_bag(self):
        '''
        Test of the taxonomy data bag.
        '''
        tdb = exposure.TaxonomyDataBag(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            damage_state=0,
            n_buildings=100.0,
            area_id='AREA # 13301',
            region='Colina',
            dwellings=107.5,
            repl_cost_usd_bdg=360000,
            population=446.5,
            name='Colina'
        )

        self.assertEqual('SARA_v1.0', tdb.schema)
        self.assertEqual('W+WS/H:1,2', tdb.taxonomy)
        self.assertEqual(0, tdb.damage_state)
        self.assertEqual(100.0, tdb.n_buildings)
        self.assertEqual('AREA # 13301', tdb.area_id)
        self.assertEqual('Colina', tdb.region)
        self.assertLess(107.4, tdb.dwellings)
        self.assertLess(tdb.dwellings, 107.6)
        self.assertEqual(360000, tdb.repl_cost_usd_bdg)
        self.assertLess(446.4, tdb.population)
        self.assertLess(tdb.population, 446.6)
        self.assertEqual('Colina', tdb.name)

    def test_fill_cell_step_by_step(self):
        '''
        Test to have an empty exposure cell
        and to add taxonomy data bags step by step
        (as it will be done in the update
        prodecure by applying the fragility functions
        and the intensities).
        '''
        tdb = exposure.TaxonomyDataBag(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            damage_state=0,
            n_buildings=100.0,
            area_id='AREA # 13301',
            region='Colina',
            dwellings=107.5,
            repl_cost_usd_bdg=360000,
            population=446.5,
            name='Colina'
        )

        geometry = wkt.loads('POINT(14 51)')
        exposure_cell = exposure.ExposureCell(
            schema='SARA_v1.0',
            name='Colina',
            gid='CHL.14.1.1_1',
            geometry=geometry,
            taxonomies=[])

        exposure_cell.add_taxonomy(tdb)

        self.assertEqual(1, len(exposure_cell.taxonomies))
        first_tax = exposure_cell.taxonomies[0]
        self.assertEqual(100.0, first_tax.n_buildings)

        # add it another time to sum up
        exposure_cell.add_taxonomy(tdb)

        self.assertEqual(1, len(exposure_cell.taxonomies))
        first_tax = exposure_cell.taxonomies[0]
        self.assertEqual(200.0, first_tax.n_buildings)

        tdb2 = exposure.TaxonomyDataBag(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            damage_state=1,
            n_buildings=100.0,
            area_id='AREA # 13301',
            region='Colina',
            dwellings=107.5,
            repl_cost_usd_bdg=360000,
            population=446.5,
            name='Colina'
        )
        exposure_cell.add_taxonomy(tdb2)
        self.assertEqual(2, len(exposure_cell.taxonomies))
        first_tax = exposure_cell.taxonomies[0]
        self.assertEqual(200.0, first_tax.n_buildings)
        second_tax = exposure_cell.taxonomies[1]
        self.assertEqual(100.0, second_tax.n_buildings)

    def test_to_empty_exposure_cell(self):
        '''
        Tests the creation of an empty
        exposure cell from an existing one.
        Should still have the same
        name, id and geometry, but no taxonomy data.
        '''
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = exposure.ExposureCell.from_simple_series(
            schema=schema,
            series=series1
        )

        empty_exposure_cell = exposure_cell1.without_taxonomies()

        self.assertEqual('Colina', empty_exposure_cell.name)
        self.assertEqual('CHL.14.1.1_1', empty_exposure_cell.gid)
        self.assertEqual(geometry1, empty_exposure_cell.geometry)
        self.assertEqual([], empty_exposure_cell.taxonomies)


if __name__ == '__main__':
    unittest.main()
