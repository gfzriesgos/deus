#!/usr/bin/env python3

import os
import json
import unittest

import geopandas as gpd
import pandas as pd
from shapely import wkt

import extendedexposure

class TestNewExposureFormat(unittest.TestCase):

    def test_exposure_cell_list_from_simple_dataframe(self):
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
        exposure_cell_list = extendedexposure.ExposureCellList.from_simple_dataframe(
            schema=schema,
            dataframe=dataframe
        )

        self.assertEqual(2, len(exposure_cell_list.get_exposure_cells()))

        recreated_dataframe = exposure_cell_list.to_simple_dataframe()

        self.assertTrue(all(dataframe['geometry'] == recreated_dataframe['geometry']))
        self.assertTrue(all(dataframe['name'] == recreated_dataframe['name']))
        self.assertTrue(all(dataframe['gc_id'] == recreated_dataframe['gc_id']))

        self.assertTrue(all(dataframe['W+WS/H:1,2'] == recreated_dataframe['W+WS/H:1,2_D0']))
        self.assertTrue(all(dataframe['W+WS/H:1,2_D1'] == recreated_dataframe['W+WS/H:1,2_D1']))



    def test_exposure_cell_list_from_dataframe(self):
        geometry1 = wkt.loads('POINT(14 51)')
        geometry2 = wkt.loads('POINT(15 52)')

        dataframe = pd.DataFrame({
            'name': ['Colina', 'Quilpue'],
            'gid': ['CHL.14.1.1_1', 'CHL.14.2.1-1'],
            'geometry': [geometry1, geometry2],
            'expo': [
                {
                    'id': [ 'AREA # 13301', 'AREA # 13301'],
                    'Region': ['Colina', 'Colina'],
                    'Taxonomy': ['W+WS/H:1,2', 'W+WS/H:1,2'],
                    'Dwellings': [107.5, 107.5],
                    'Buildings': [100.0, 50.0],
                    'Repl_cost_USD/bdg': [360000, 450000],
                    'Population': [446.5, 446.5],
                    'name': ['Colina', 'Colina'],
                    'Damage': ['D0', 'D1']
                },
                {
                    'id': [ 'AREA # 13302', 'AREA # 13302'],
                    'Region': ['Quilpue', 'Quilpue'],
                    'Taxonomy': ['W+WS/H:1,2', 'W+WS/H:1,2'],
                    'Dwellings': [107.5, 107.5],
                    'Buildings': [80.0, 55.0],
                    'Repl_cost_USD/bdg': [360000, 450000],
                    'Population': [446.5, 446.5],
                    'name': ['Quilpue', 'Quilpue'],
                    'Damage': ['D0', 'D1']
                }
            ]
        })
        schema = 'SARA_v1.0'
        exposure_cell_list = extendedexposure.ExposureCellList.from_dataframe(
            schema=schema,
            dataframe=dataframe
        )

        self.assertEqual(2, len(exposure_cell_list.get_exposure_cells()))

        recreated_dataframe = exposure_cell_list.to_dataframe()

        self.assertTrue(all(dataframe['geometry'] == recreated_dataframe['geometry']))
        self.assertTrue(all(dataframe['name'] == recreated_dataframe['name']))
        self.assertTrue(all(dataframe['gid'] == recreated_dataframe['gid']))
        self.assertTrue(all(dataframe['expo'] == recreated_dataframe['expo']))




    def test_exposure_cell_list(self):
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = extendedexposure.ExposureCell.from_simple_series(schema, series1)

        geometry2 = wkt.loads('POINT(15 52)')
        series2 = pd.Series({
            'name': 'Quilpue',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry2,
            'W+WS/H:1,2': 80.0,
            'W+WS/H:1.2_D1': 30.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell2 = extendedexposure.ExposureCell.from_simple_series(schema, series2)

        exposure_cell_list = extendedexposure.ExposureCellList(exposure_cells=[exposure_cell1, exposure_cell2])

        self.assertEqual(2, len(exposure_cell_list.get_exposure_cells()))


    def test_exposure_cell_from_simple_series(self):
        geometry = wkt.loads('POINT(14 51)')
        series = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell = extendedexposure.ExposureCell.from_simple_series(schema, series)

        self.assertEqual('SARA_v1.0',  exposure_cell.get_schema())
        self.assertEqual('CHL.14.1.1_1', exposure_cell.get_gid())
        self.assertEqual('Colina', exposure_cell.get_name())
        self.assertEqual(geometry, exposure_cell.get_geometry())
        lon, lat = exposure_cell.get_lon_lat_of_centroid()
        self.assertEqual(14, lon)
        self.assertEqual(51, lat)
        self.assertEqual(2, len(exposure_cell.get_taxonomies()))
        first_tax = exposure_cell.get_taxonomies()[0]
        self.assertEqual(0, first_tax.get_damage_state())
        second_tax = exposure_cell.get_taxonomies()[1]
        self.assertEqual(1, second_tax.get_damage_state())
        

    def test_exposure_cell_from_series(self):
        geometry = wkt.loads('POINT(14 51)')
        series = pd.Series({
            'name': 'Colina',
            'gid': 'CHL.14.1.1_1',
            'geometry': geometry,
            'expo': {
                'id': [ 'AREA # 13301', 'AREA # 13301'],
                'Region': ['Colina', 'Colina'],
                'Taxonomy': ['W+WS/H:1,2', 'W+WS/H:1,2'],
                'Dwellings': [107.5, 107.5],
                'Buildings': [100.0, 50.0],
                'Repl_cost_USD/bdg': [360000, 450000],
                'Population': [446.5, 446.5],
                'name': ['Colina', 'Colina'],
                'Damage': ['D0', 'D1']
            }
        })

        schema = 'SARA_v1.0'
        exposure_cell = extendedexposure.ExposureCell.from_series(schema, series)

        self.assertEqual('SARA_v1.0',  exposure_cell.get_schema())
        self.assertEqual('CHL.14.1.1_1', exposure_cell.get_gid())
        self.assertEqual('Colina', exposure_cell.get_name())
        self.assertEqual(geometry, exposure_cell.get_geometry())
        lon, lat = exposure_cell.get_lon_lat_of_centroid()
        self.assertEqual(14, lon)
        self.assertEqual(51, lat)
        self.assertEqual(2, len(exposure_cell.get_taxonomies()))
        first_tax = exposure_cell.get_taxonomies()[0]
        self.assertEqual(0, first_tax.get_damage_state())
        second_tax = exposure_cell.get_taxonomies()[1]
        self.assertEqual(1, second_tax.get_damage_state())

    def test_exposure_cell(self):
        tdb1 = extendedexposure.TaxonomyDataBag(
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
        tdb2 = extendedexposure.TaxonomyDataBag(
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
        exposure_cell = extendedexposure.ExposureCell(
            schema='SARA_v1.0',
            gid='CHL.14.1.1_1',
            name='Colina',
            geometry=geometry,
            taxonomies =[tdb1, tdb2]
        )
        
        self.assertEqual('SARA_v1.0',  exposure_cell.get_schema())
        self.assertEqual('CHL.14.1.1_1', exposure_cell.get_gid())
        self.assertEqual('Colina', exposure_cell.get_name())
        self.assertEqual(geometry, exposure_cell.get_geometry())
        lon, lat = exposure_cell.get_lon_lat_of_centroid()
        self.assertEqual(14, lon)
        self.assertEqual(51, lat)
        self.assertEqual(2, len(exposure_cell.get_taxonomies()))


    def test_extract_taxonomy_from_taxonomy_damage_state_string(self):
        self.assertEqual(0, extendedexposure.extract_damage_state_from_taxonomy_damage_state_string('W+WS/H:1,2'))
        self.assertEqual(2, extendedexposure.extract_damage_state_from_taxonomy_damage_state_string('W+WS/H:1,2_D2'))

    def test_extract_taxonomy_from_taxonomy_damage_state_string(self):
        self.assertEqual('W+WS/H:1,2', extendedexposure.extract_taxonomy_from_taxonomy_damage_state_string('W+WS/H:1,2'))
        self.assertEqual('W+WS/H:1,2', extendedexposure.extract_taxonomy_from_taxonomy_damage_state_string('W+WS/H:1,2_D2'))

    def test_taxonomy_data_bag_from_simple_series(self):
        series = pd.Series({
            'W+WS/H:1,2_D3': 100.0,
            'name': 'Colina',
            'gid': 'xyz123',
            # won't be used here
            'geometry': 'POINT(1 1)',
        })

        schema = 'SARA_v1.0'
        tdb = extendedexposure.TaxonomyDataBag.from_simple_series(series, 'W+WS/H:1,2_D3', schema)

        self.assertEqual('SARA_v1.0', tdb.get_schema())
        self.assertEqual('W+WS/H:1,2', tdb.get_taxonomy())
        self.assertEqual(3, tdb.get_damage_state())
        self.assertEqual(100.0, tdb.get_n_buildings())
        self.assertEqual('Colina', tdb.get_name())



    def test_remove_prefix_d_for_damage_state(self):
        self.assertEqual(0, extendedexposure.remove_prefix_d_for_damage_state('D0'))
        self.assertEqual(1, extendedexposure.remove_prefix_d_for_damage_state('D1'))
        self.assertEqual(10, extendedexposure.remove_prefix_d_for_damage_state('D10'))

    def test_taxonomy_data_bag_from_series(self):
        series = pd.Series({
            'id': 'AREA # 13301',
            'Region': 'Colina',
            'Taxonomy': 'W+WS/H:1,2',
            'Dwellings': 107.5,
            'Buildings': 100.0,
            'Repl_cost_USD/bdg': 360000,
            'Population': 446.5,
            'name': 'Colina',
            'Damage': 'D0'
        })

        schema = 'SARA_v1.0'

        tdb = extendedexposure.TaxonomyDataBag.from_series(
                series, schema)

        self.assertEqual('SARA_v1.0', tdb.get_schema())
        self.assertEqual('W+WS/H:1,2', tdb.get_taxonomy())
        self.assertEqual(0, tdb.get_damage_state())
        self.assertEqual(100.0, tdb.get_n_buildings())
        self.assertEqual('AREA # 13301', tdb.get_area_id())
        self.assertEqual('Colina', tdb.get_region())
        self.assertLess(107.4, tdb.get_dwellings())
        self.assertLess(tdb.get_dwellings(), 107.6)
        self.assertEqual(360000, tdb.get_repl_cost_usd_bdg())
        self.assertLess(446.4, tdb.get_population())
        self.assertLess(tdb.get_population(), 446.6)
        self.assertEqual('Colina', tdb.get_name())

    def test_taxonomy_data_bag(self):
        tdb = extendedexposure.TaxonomyDataBag(
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

        self.assertEqual('SARA_v1.0', tdb.get_schema())
        self.assertEqual('W+WS/H:1,2', tdb.get_taxonomy())
        self.assertEqual(0, tdb.get_damage_state())
        self.assertEqual(100.0, tdb.get_n_buildings())
        self.assertEqual('AREA # 13301', tdb.get_area_id())
        self.assertEqual('Colina', tdb.get_region())
        self.assertLess(107.4, tdb.get_dwellings())
        self.assertLess(tdb.get_dwellings(), 107.6)
        self.assertEqual(360000, tdb.get_repl_cost_usd_bdg())
        self.assertLess(446.4, tdb.get_population())
        self.assertLess(tdb.get_population(), 446.6)
        self.assertEqual('Colina', tdb.get_name())

    def test_fill_cell_step_by_step(self):
        tdb = extendedexposure.TaxonomyDataBag(
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
        exposure_cell = extendedexposure.ExposureCell(
            schema='SARA_v1.0',
            name='Colina',
            gid='CHL.14.1.1_1',
            geometry=geometry,
            taxonomies=[])

        exposure_cell.add_taxonomy(tdb)

        self.assertEqual(1, len(exposure_cell.get_taxonomies()))
        first_tax = exposure_cell.get_taxonomies()[0]
        self.assertEqual(100.0, first_tax.get_n_buildings())

        # add it another time to sum up
        exposure_cell.add_taxonomy(tdb)

        self.assertEqual(1, len(exposure_cell.get_taxonomies()))
        first_tax = exposure_cell.get_taxonomies()[0]
        self.assertEqual(200.0, first_tax.get_n_buildings())

        tdb2 = extendedexposure.TaxonomyDataBag(
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
        self.assertEqual(2, len(exposure_cell.get_taxonomies()))
        first_tax = exposure_cell.get_taxonomies()[0]
        self.assertEqual(200.0, first_tax.get_n_buildings())
        second_tax = exposure_cell.get_taxonomies()[1]
        self.assertEqual(100.0, second_tax.get_n_buildings())

    def test_to_empty_exposure_cell(self):
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = extendedexposure.ExposureCell.from_simple_series(schema, series1)

        empty_exposure_cell = exposure_cell1.without_taxonomies()

        self.assertEqual('Colina', empty_exposure_cell.get_name())
        self.assertEqual('CHL.14.1.1_1', empty_exposure_cell.get_gid())
        self.assertEqual(geometry1, empty_exposure_cell.get_geometry())
        self.assertEqual([], empty_exposure_cell.get_taxonomies())

    def test_exposure_to_transition_cell(self):
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = extendedexposure.ExposureCell.from_simple_series(schema, series1)
        transition_cell1 = extendedexposure.TransitionCell.from_exposure_cell(exposure_cell1)

        self.assertEqual(0, len(transition_cell1.get_transitions()))

        transition_to_add = extendedexposure.Transition(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            from_damage_state=0,
            to_damage_state=1,
            n_buildings=10,
        )
        transition_cell1.add_transition(transition_to_add)

        self.assertEqual(1, len(transition_cell1.get_transitions()))
        first_transition = transition_cell1.get_transitions()[0]

        self.assertEqual(schema, first_transition.get_schema())
        self.assertEqual('W+WS/H:1,2', first_transition.get_taxonomy())
        self.assertEqual(0, first_transition.get_from_damage_state())
        self.assertEqual(1, first_transition.get_to_damage_state())
        self.assertEqual(10, first_transition.get_n_buildings())

        transition_cell1.add_transition(transition_to_add)

        self.assertEqual(1, len(transition_cell1.get_transitions()))
        first_transition = transition_cell1.get_transitions()[0]
        self.assertEqual(20, first_transition.get_n_buildings())

        self.assertEqual('Colina', transition_cell1.get_name())
        self.assertEqual('CHL.14.1.1_1', transition_cell1.get_gid())
        self.assertEqual(geometry1, transition_cell1.get_geometry())

        transition_to_add2 = extendedexposure.Transition(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            from_damage_state=0,
            to_damage_state=2,
            n_buildings=10,
        )
        transition_cell1.add_transition(transition_to_add2)

        transition_list = extendedexposure.TransitionCellList([transition_cell1])
        transition_dataframe = transition_list.to_dataframe()

        self.assertEqual('Colina', transition_dataframe['name'][0])
        self.assertEqual('CHL.14.1.1_1', transition_dataframe['gid'][0])
        self.assertEqual(geometry1, transition_dataframe['geometry'][0])
        self.assertEqual(schema, transition_dataframe['schema'][0])
        
        transition_element = pd.DataFrame(transition_dataframe['transitions'][0])

        self.assertTrue('taxonomy' in transition_element.columns)
        self.assertTrue('from_damage_state' in transition_element.columns)
        self.assertTrue('to_damage_state' in transition_element.columns)
        self.assertTrue('n_buildings' in transition_element.columns)

        self.assertEqual(2, len(transition_element['taxonomy']))
        self.assertTrue(all(transition_element['taxonomy'] == 'W+WS/H:1,2'))
        self.assertTrue(all(transition_element['from_damage_state'] == 0))
        self.assertTrue(any(transition_element['to_damage_state'] == 1))
        self.assertTrue(any(transition_element['to_damage_state'] == 2))


    def test_exposure_to_loss_cell(self):
        geometry1 = wkt.loads('POINT(14 51)')
        series1 = pd.Series({
            'name': 'Colina',
            'gc_id': 'CHL.14.1.1_1',
            'geometry': geometry1,
            'W+WS/H:1,2': 100.0,
            'W+WS/H:1.2_D1': 50.0,
        })
        schema = 'SARA_v1.0'
        exposure_cell1 = extendedexposure.ExposureCell.from_simple_series(schema, series1)
        transition_cell1 = extendedexposure.TransitionCell.from_exposure_cell(exposure_cell1)

        transition_to_add = extendedexposure.Transition(
            schema='SARA_v1.0',
            taxonomy='W+WS/H:1,2',
            from_damage_state=0,
            to_damage_state=1,
            n_buildings=10,
        )

        transition_cell1.add_transition(transition_to_add)
        loss_cell1 = extendedexposure.LossCell.from_transition_cell(
            transition_cell1,
            DummyLossProvider()
        )

        self.assertEqual('$', loss_cell1.get_loss_unit())
        self.assertEqual(10, loss_cell1.get_loss_value())
        self.assertEqual('Colina', loss_cell1.get_name())
        self.assertEqual('CHL.14.1.1_1', loss_cell1.get_gid())
        self.assertEqual(geometry1, loss_cell1.get_geometry())

        loss_list = extendedexposure.LossCellList([loss_cell1])

        loss_dataframe = loss_list.to_dataframe()

        self.assertEqual(geometry1, loss_dataframe['geometry'][0])
        self.assertEqual('Colina', loss_dataframe['name'][0])
        self.assertEqual(10, loss_dataframe['loss_value'][0])
        self.assertEqual('$', loss_dataframe['loss_unit'][0])


class DummyLossProvider():

    #def get_loss(self, schema, taxonomy, from_damage_state, to_damage_state):
    def get_loss(self, *args, **kwargs):
        return 1

    def get_unit(self):
        return '$'



if __name__ == '__main__':
    unittest.main()
