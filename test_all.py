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

import intensitydatawrapper
import intensityprovider
import damage
import exposure
import fragility
import schemamapping
import rasterwrapper
import shakemap


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
                'id': 'SARA.0',
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

        self.assertEqual('SARA.0', schema)
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
                'id': 'SARA.0',
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

        empty_exposure_cell = exposure_cell.new_prototype('SARA.0')

        lon2, lat2 = empty_exposure_cell.get_lon_lat_of_centroid()

        self.assertEqual(lon, lon2)
        self.assertEqual(lat, lat2)

        self.assertEqual(
            empty_exposure_cell.get_series()['name'],
            'example point1')

        taxonomies = exposure_cell.get_taxonomies()

        self.assertIn(
            # the backslashes are removed
            exposure.Taxonomy(name=r'MCF/DNO/_1', count=6, schema='SARA.0'),
            taxonomies
        )

    def test_exposure_taxonomy_damage_state(self):
        """
        Test exposure taxonomy damage state
        :return: None
        """
        tax1 = exposure.Taxonomy(
            name=r'MCF\/DNO\/_1',
            count=6,
            schema='SARA.0')

        ds1 = tax1.get_damage_state()

        self.assertEqual(ds1, 0)

        tax2 = exposure.Taxonomy(
            name=r'MCF\/DNO\/_1_D1',
            count=6,
            schema='SARA.0')

        ds2 = tax2.get_damage_state()

        self.assertEqual(ds2, 1)

        tax3 = exposure.Taxonomy(
            name=r'MCF\/DNO\/_1_D5',
            count=6,
            schema='SARA.0')

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
        damage_state_mapper = schemamapping.DamageStateMapper(mapping_data)

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

        damage_state_mapper = schemamapping.DamageStateMapper.from_files(files)
        self.assertIsNotNone(damage_state_mapper)

    def test_building_class_mapping(self):
        '''
        Test the mapping of one building class to another.
        :return: None
        '''

        # the names and the data here are mostly
        # fantasy values
        mapping_data = [
            {
                'source_name': 'ems_98',
                'target_name': 'sup_13',
                'conv_matrix': {
                    'URM': {
                        'WOOD': 0.2,
                        'RC': 0.8,
                    },
                },
            },
        ]

        building_class_mapper = schemamapping.BuildingClassMapper(mapping_data)

        result_urm_ems_to_ems = building_class_mapper.map_building_class(
            source_building_class='URM',
            source_name='ems_98',
            target_name='ems_98',
            n_buildings=100.0
        )

        self.assertEqual(1, len(result_urm_ems_to_ems))
        self.assertEqual('URM', result_urm_ems_to_ems[0].get_building_class())
        self.assertLess(99.9999, result_urm_ems_to_ems[0].get_n_buildings())
        self.assertLess(result_urm_ems_to_ems[0].get_n_buildings(), 100.0001)

        result_urm_ems_to_sup = building_class_mapper.map_building_class(
            source_building_class='URM',
            source_name='ems_98',
            target_name='sup_13',
            n_buildings=100.0
        )

        self.assertEqual(2, len(result_urm_ems_to_sup))
        result_urm_ems_to_sup_wood = [
            x for x in result_urm_ems_to_sup
            if x.get_building_class() == 'WOOD'][0]
        result_urm_ems_to_sup_rc = [
            x for x in result_urm_ems_to_sup
            if x.get_building_class() == 'RC'][0]

        self.assertLess(19.999, result_urm_ems_to_sup_wood.get_n_buildings())
        self.assertLess(result_urm_ems_to_sup_wood.get_n_buildings(), 20.001)

        self.assertLess(79.999, result_urm_ems_to_sup_rc.get_n_buildings())
        self.assertLess(result_urm_ems_to_sup_rc.get_n_buildings(), 81.001)

    def test_read_shakemap(self):
        '''
        Reads a normal shakemap (as it is the output of shakyground.
        :return: None
        '''
        shake_map_eq = shakemap.Shakemaps.from_file(
            './testinputs/shakemap.xml')
        eq_provider = shake_map_eq.to_intensity_provider()

        self.assertIsNotNone(eq_provider)

        eq_intensity, eq_units = eq_provider.get_nearest(
            lon=-71.2, lat=-32.65)

        self.assertEqual('g', eq_units['PGA'])

        self.assertLess(0.06327, eq_intensity['PGA'])
        self.assertLess(eq_intensity['PGA'], 0.06328)

        shake_map_ts = shakemap.Shakemaps.from_file(
            './testinputs/shakemap_tsunami.xml')
        ts_provider = shake_map_ts.to_intensity_provider()

        ts_intensity, ts_units = ts_provider.get_nearest(
            lon=-71.547, lat=-32.803)

        self.assertEqual('m', ts_units['MWH'])

        self.assertLess(3.5621, ts_intensity['MWH'])
        self.assertLess(ts_intensity['MWH'], 3.5623)

    def test_schema_mapping(self):
        '''
        Maps a building class with damage states to other
        building classes and damage states.
        :return: None
        '''

        bc_mapping_data = [
            {
                'source_name': 'ems_98',
                'target_name': 'sup_13',
                'conv_matrix': {
                    'URM': {
                        'WOOD': 0.2,
                        'RC': 0.8,
                    },
                },
            }
        ]

        building_class_mapper = schemamapping.BuildingClassMapper(
            bc_mapping_data)

        ds_mapping_data = [
            {
                'source_name': 'ems_98',
                'target_name': 'sup_13',
                'conv_matrix': {
                    '5': {
                        '5': 0.5,
                        '6': 0.5,
                    },
                },
            },
        ]

        damage_state_mapper = schemamapping.DamageStateMapper(ds_mapping_data)

        schema_mapper = schemamapping.SchemaMapper(
            building_class_mapper, damage_state_mapper)

        result_mapping_in_schema = schema_mapper.map_schema(
            source_building_class='URM',
            source_damage_state=5,
            source_name='ems_98',
            target_name='ems_98',
            n_buildings=100.0
        )

        self.assertEqual(1, len(result_mapping_in_schema))
        self.assertEqual(
            'URM',
            result_mapping_in_schema[0].get_building_class())
        self.assertEqual(5, result_mapping_in_schema[0].get_damage_state())

        self.assertLess(99.9, result_mapping_in_schema[0].get_n_buildings())
        self.assertLess(result_mapping_in_schema[0].get_n_buildings(), 100.1)

        result_mapping_to_sup = schema_mapper.map_schema(
            source_building_class='URM',
            source_damage_state=5,
            source_name='ems_98',
            target_name='sup_13',
            n_buildings=100.0
        )

        self.assertEqual(4, len(result_mapping_to_sup))

        res_wood_5 = [
            x for x in result_mapping_to_sup
            if x.get_building_class() == 'WOOD'
            and x.get_damage_state() == 5][0]

        self.assertLess(9.9, res_wood_5.get_n_buildings())
        self.assertLess(res_wood_5.get_n_buildings(), 10.1)

        res_wood_6 = [
            x for x in result_mapping_to_sup
            if x.get_building_class() == 'WOOD'
            and x.get_damage_state() == 6][0]

        self.assertLess(9.9, res_wood_6.get_n_buildings())
        self.assertLess(res_wood_6.get_n_buildings(), 10.1)

        res_rc_5 = [
            x for x in result_mapping_to_sup
            if x.get_building_class() == 'RC'
            and x.get_damage_state() == 5][0]

        self.assertLess(39.9, res_rc_5.get_n_buildings())
        self.assertLess(res_rc_5.get_n_buildings(), 40.1)

        res_rc_6 = [
            x for x in result_mapping_to_sup
            if x.get_building_class() == 'RC'
            and x.get_damage_state() == 6][0]

        self.assertLess(39.9, res_rc_6.get_n_buildings())
        self.assertLess(res_rc_6.get_n_buildings(), 40.1)

    def test_read_schema_from_fragility_file(self):
        '''
        Reads the schema from the fragility file.
        '''

        fr_file = fragility.Fragility.from_file(
            './testinputs/fragility_sara.json')
        fr_provider = fr_file.to_fragility_provider()

        schema = fr_provider.get_schema()

        self.assertEqual('SARA.0', schema)

        fr_file2 = fragility.Fragility.from_file(
            './testinputs/fragility_supparsi.json')
        fr_provider2 = fr_file2.to_fragility_provider()

        schema2 = fr_provider2.get_schema()

        self.assertEqual('SUPPARSI_2013.0', schema2)

    def test_cell_mapping(self):
        '''
        Tests the schema mapping with a exposure
        cell.
        :return: None
        '''
        exposure_cell = get_exposure_cell_for_sara()

        schema_mapper = get_schema_mapper_for_sara_to_supparsi()

        mapped_exposure_cell = exposure_cell.map_schema(
            'SUPPARSI_2013.0', schema_mapper)

        new_schema = mapped_exposure_cell.get_schema()

        self.assertEqual('SUPPARSI_2013.0', new_schema)

        new_series = mapped_exposure_cell.get_series()

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

    def test_schema_mapping_with_data_specific_for_each_building_class(self):
        '''
        Also tests the mapping process, but this time it uses
        data specific to each building class for the mapping process.
        :return: None
        '''

        mapping_data = [
            {
                "source_name": "SARA_CR_LDUAL_DUC_H_8_19",
                "target_name": "Supparsi_2013_RC2",
                "source_damage_states": [0, 1, 2, 3, 4],
                "target_damage_states": [0, 1, 2, 3, 4, 5, 6],
                "conv_matrix": {
                    "0": {
                        "0": 0.0000000142,
                        "1": 0.0000000008,
                        "2": 0.0,
                        "3": 2.212268738e-20,
                        "4": 6.212234209e-21
                    },
                    "1": {
                        "0": 0.8390575513,
                        "1": 0.048000721,
                        "2": 0.0526925393,
                        "3": 0.0000000162,
                        "4": 0.0000000282
                    },
                    "2": {
                        "0": 0.1609360831,
                        "1": 0.0740190246,
                        "2": 0.2988759267,
                        "3": 0.0000040603,
                        "4": 0.0000432286
                    },
                    "3": {
                        "0": 0.00000635,
                        "1": 0.8322648472,
                        "2": 0.6103666121,
                        "3": 0.6048565672,
                        "4": 0.4031390361
                    },
                    "4": {
                        "0": 0.0000000014,
                        "1": 0.0119080503,
                        "2": 0.0380006473,
                        "3": 0.0990358442,
                        "4": 0.1554193652
                    },
                    "5": {
                        "0": 7.794059135e-20,
                        "1": 0.0007803014,
                        "2": 0.0000625369,
                        "3": 0.06054086,
                        "4": 0.196956846
                    },
                    "6": {
                        "0": 3.174351391e-21,
                        "1": 0.0330270548,
                        "2": 0.0000017377,
                        "3": 0.2355626521,
                        "4": 0.2444414959
                    }
                }
            },
            {
                "source_name": "SARA_CR_LDUAL_DUC_H_8_19",
                "target_name": "Supparsi_2013_RC1",
                "source_damage_states": [0, 1, 2, 3, 4],
                "target_damage_states": [0, 1, 2, 3, 4, 5, 6],
                "conv_matrix": {
                    "0": {
                        "0": 0.0000000142,
                        "1": 0.0000000008,
                        "2": 0.0,
                        "3": 2.212268738e-20,
                        "4": 6.212234209e-21
                    },
                    "1": {
                        "0": 0.8390575513,
                        "1": 0.048000721,
                        "2": 0.0526925393,
                        "3": 0.0000000162,
                        "4": 0.0000000282
                    },
                    "2": {
                        "0": 0.1609360831,
                        "1": 0.0740190246,
                        "2": 0.2988759267,
                        "3": 0.0000040603,
                        "4": 0.0000432286
                    },
                    "3": {
                        "0": 0.00000635,
                        "1": 0.8322648472,
                        "2": 0.6103666121,
                        "3": 0.6048565672,
                        "4": 0.4031390361
                    },
                    "4": {
                        "0": 0.0000000014,
                        "1": 0.0119080503,
                        "2": 0.0380006473,
                        "3": 0.0990358442,
                        "4": 0.1554193652
                    },
                    "5": {
                        "0": 7.794059135e-20,
                        "1": 0.0007803014,
                        "2": 0.0000625369,
                        "3": 0.06054086,
                        "4": 0.196956846
                    },
                    "6": {
                        "0": 3.174351391e-21,
                        "1": 0.0330270548,
                        "2": 0.0000017377,
                        "3": 0.2355626521,
                        "4": 0.2444414959
                    }
                }
            }
        ]

        schema_mapper = schemamapping \
            .BuildingClassSpecificDamageStateMapper \
            .from_list_of_dicts(mapping_data)

        exposure_cell_data = gpd.GeoDataFrame(pd.DataFrame({
            'geometry': ['POINT(12.0 15.0)'],
            'name': ['example point1'],
            'gc_id': ['abcdefg'],
            'CR_LDUAL_DUC_H_8_19': [100.0]
        }))
        exposure_cell_data['geometry'] = exposure_cell_data['geometry'].apply(
            wkt.loads)
        exposure_cell_series = exposure_cell_data.iloc[0]

        exposure_cell = exposure.ExposureCell(exposure_cell_series, 'SARA')

        mapped_exposure_cell = exposure_cell.map_schema(
            'Supparsi_2013',
            schema_mapper
        )

        self.assertEqual('Supparsi_2013', mapped_exposure_cell.get_schema())

        new_series = mapped_exposure_cell.get_series()
        # there are only two aim building classes
        # (and both with same data for the mapping)
        # and the mappings here are picked randomly
        # from the provided mapping files
        # --> the mapping here is neither complete nor
        # it is the expected one for the chosen building
        # classes

        self.assertLess(1.41e-6, new_series['RC1_D0'])
        self.assertLess(new_series['RC1_D0'], 1.43e-6)

        self.assertLess(7.9e-8, new_series['RC1_D1'])
        self.assertLess(new_series['RC1_D1'], 8.1e-8)

        self.assertEqual(0, new_series['RC1_D2'])

        self.assertLess(2.20e-18, new_series['RC1_D3'])
        self.assertLess(new_series['RC1_D3'], 2.22e-18)

        self.assertLess(6.211e-19, new_series['RC1_D4'])
        self.assertLess(new_series['RC1_D4'], 6.213e-19)

        self.assertLess(1.41e-6, new_series['RC2_D0'])
        self.assertLess(new_series['RC2_D0'], 1.43e-6)

        self.assertLess(7.9e-8, new_series['RC2_D1'])
        self.assertLess(new_series['RC2_D1'], 8.1e-8)

        self.assertEqual(0, new_series['RC2_D2'])

        self.assertLess(2.20e-18, new_series['RC2_D3'])
        self.assertLess(new_series['RC2_D3'], 2.22e-18)

        self.assertLess(6.211e-19, new_series['RC2_D4'])
        self.assertLess(new_series['RC2_D4'], 6.213e-19)

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
                'id': 'SARA.0',
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

        updated_series = updated_exposure_cell.get_series()

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

        transition_series = transition_cell.get_series()

        self.assertEqual(updated_series['gc_id'], transition_series['gc_id'])
        self.assertEqual(
            updated_series['geometry'],
            transition_series['geometry'])
        self.assertEqual(
            updated_series['name'],
            transition_series['name'])

        updates_mur_h1 = transition_series['MUR_H1']

        updates_mur_h1_0_1 = [
            x for x in updates_mur_h1
            if x['from'] == 0
            and x['to'] == 1][0]

        self.assertLess(0.022, updates_mur_h1_0_1['n_buildings'])
        self.assertLess(updates_mur_h1_0_1['n_buildings'], 0.023)

        # the other mur updates are similar, not so fancy anyway

        updates_er_etr_h1_2 = transition_series['ER_ETR_H1_2']

        updates_er_etr_h1_2_2_3 = [
            x for x in updates_er_etr_h1_2
            if x['from'] == 2
            and x['to'] == 3][0]

        self.assertLess(43.87, updates_er_etr_h1_2_2_3['n_buildings'])
        self.assertLess(updates_er_etr_h1_2_2_3['n_buildings'], 43.88)

        updates_er_etr_h1_2_2_4 = [
            x for x in updates_er_etr_h1_2
            if x['from'] == 2
            and x['to'] == 4][0]

        self.assertLess(153.38, updates_er_etr_h1_2_2_4['n_buildings'])
        self.assertLess(updates_er_etr_h1_2_2_4['n_buildings'], 153.39)

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

    def test_damage_computation(self):
        '''
        Test for the damage computation.
        :return: None
        '''
        damage_data = {
            'data': [
                {
                    'taxonomy': 'URM',
                    'loss_matrix': {
                        '0': {
                            '1': 500,
                            '2': 600,
                            '3': 700,
                            '4': 800,
                        }
                    }
                }
            ]
        }

        damage_provider = damage.DamageProvider(damage_data)

        damage_value = damage_provider.get_damage_for_transition(
            building_class='URM',
            from_damage_state=0,
            to_damage_state=3
        )

        self.assertEqual(700, damage_value)

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
    return exposure.ExposureCell(series, 'SARA.0')


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

    return exposure.ExposureCell(exposure_cell_series, 'SARA.0')


def get_schema_mapper_for_sara_to_supparsi():
    '''
    Returns the mapper from sara to supparsi.
    '''
    bc_mapping_data = [
        {
            'source_name': 'SARA.0',
            'target_name': 'SUPPARSI_2013.0',
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
            'source_name': 'SARA.0',
            'target_name': 'SUPPARSI_2013.0',
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
