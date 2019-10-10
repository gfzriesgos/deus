#!/usr/bin/env python3

import glob
import os
import unittest

import geopandas as gpd
import pandas as pd

from shapely import wkt

import schemamapping
import exposure


class TestSchemaMapping(unittest.TestCase):

    def test_schema_mapping_with_data_specific_for_each_building_class(self):
        '''
        Also tests the mapping process, but this time it uses
        data specific to each building class for the mapping process.
        :return: None
        '''

        mapping_data = [
            {
                "source_schema": "SARA",
                "source_taxonomy": "CR_LDUAL_DUC_H_8_19",
                "target_schema": "Suppasri_2013",
                "target_taxonomy": "RC2",
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
                "source_schema": "SARA",
                "source_taxonomy": "CR_LDUAL_DUC_H_8_19",
                "target_schema": "Suppasri_2013",
                "target_taxonomy": "RC1",
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

        exposure_cell = exposure.ExposureCell.from_simple_series(
            series=exposure_cell_series,
            schema='SARA'
        )

        mapped_exposure_cell = exposure_cell.map_schema(
            'Suppasri_2013',
            schema_mapper
        )

        self.assertEqual('Suppasri_2013', mapped_exposure_cell.get_schema())

        new_series = mapped_exposure_cell.to_simple_series()
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


if __name__ == '__main__':
    unittest.main()
