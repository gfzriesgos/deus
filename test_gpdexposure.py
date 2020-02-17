#!/usr/bin/env python3

"""
This is a test file for the pure geopandas implementation
of the exposure handling.
"""

import unittest

import geopandas
import pandas
import shapely.wkt

import testimplementations

import gpdexposure
import fragility
import schemamapping


class TestGpdExposureDamageStateUpdate(unittest.TestCase):
    """
    This is a test class for the gpdexposure module.
    """

    def setUp(self):
        """
        This implementation uses the same base data
        as the test_performace_optimization.py.
        But in this case we want to test the
        gpdexposure module.
        """
        # lets say we have 400 buildings
        # TAX1 D0 with 100
        # TAX1 D1 with 100
        # TAX2 D0 with 100
        # TAX2 D1 with 100

        expo = {
            'Taxonomy': ['TAX1', 'TAX1', 'TAX2', 'TAX2'],
            'Damage': ['D0', 'D1', 'D0', 'D1'],
            'Buildings': [100.0, 100.0, 100.0, 100.0]
        }

        series = pandas.Series({
            'gid': '001',
            'geometry': shapely.wkt.loads('POINT(52 15)'),
            'expo': expo
        })

        self.old_exposure = pandas.DataFrame([series])

        self.fake_intensity_provider = (
            testimplementations
            .AlwaysTheSameIntensityProvider(
                'INTENSITY', 1, 'unitless'
            )
        )

        fragility_data = {
            'meta': {
                'id': 'SCHEMA1',
                # we will make the implementation
                # think that we do the normal way
                # but we will mock it later
                # so shape and values does not matter that
                # much
                # the function that we want to
                # use will be defined
                # to just return the _mean
                # value as probability
                # so no matter
                # what intensity is given
                'shape': 'different!!!',
            },
            'data': [
                {
                    'imt': 'intensity',
                    'imu': 'unitless',
                    # half of the buildings go into D1
                    'D1_mean': 0.5,
                    'D1_stddev': 0,
                    # 25% go into D2
                    'D2_mean': 0.25,
                    'D2_stddev': 0,
                    # there are no other values for
                    # D1 to D2
                    'taxonomy': 'TAX1',
                },
                {
                    'imt': 'intensity',
                    'imu': 'unitless',
                    # 75% go into D1
                    'D1_mean': 0.75,
                    'D1_stddev': 0,
                    # 40% go into D2
                    'D2_mean': 0.4,
                    'D2_stddev': 0,
                    'taxonomy': 'TAX2',
                },

            ]
        }

        fragility_data2 = {
            'meta': {
                'id': 'SCHEMA2',
                # we will make the implementation
                # think that we do the normal way
                # but we will mock it later
                # so shape and values does not matter that
                # much
                # the function that we want to
                # use will be defined
                # to just return the _mean
                # value as probability
                # so no matter
                # what intensity is given
                'shape': 'different!!!',
            },
            'data': [
                {
                    'imt': 'intensity',
                    'imu': 'unitless',
                    # half of the buildings go into D1
                    'D1_mean': 0.75,
                    'D1_stddev': 0,
                    # 25% go into D2
                    'D2_mean': 0.4,
                    'D2_stddev': 0,
                    'D3_mean': 0.2,
                    'D3_stddev': 0,
                    # there are no other values for
                    # D1 to D2
                    'taxonomy': 'TAX',
                },

            ]
        }

        self.fake_fragility_provider = fragility.Fragility(
            fragility_data
        ).to_fragility_provider_with_specified_fragility_function(
            MakeFakeFunction
        )
        # and another one for the schema mapping too
        self.fake_fragility_provider2 = fragility.Fragility(
            fragility_data2
        ).to_fragility_provider_with_specified_fragility_function(
            MakeFakeFunction
        )

        tax_schema_mapping_data = [
            {
                'source_schema': 'SCHEMA1',
                'target_schema': 'SCHEMA2',
                'conv_matrix': {
                    'TAX1': {
                        'TAX': 1.0,
                    },
                    'TAX2': {
                        'TAX': 1.0,
                    }
                }
            }
        ]

        ds_schema_mapping_data = [
            {
                'source_schema': 'SCHEMA1',
                'target_schema': 'SCHEMA2',
                'source_taxonomy': 'TAX1',
                'target_taxonomy': 'TAX',
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                        '2': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.5,
                        '2': 0.2,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.3,
                        '2': 0.3,
                    },
                    '3': {
                        '0': 0.0,
                        '1': 0.2,
                        '2': 0.5,
                    }
                }
            },
            {
                'source_schema': 'SCHEMA1',
                'target_schema': 'SCHEMA2',
                'source_taxonomy': 'TAX2',
                'target_taxonomy': 'TAX',
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                        '2': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.9,
                        '2': 0.1,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.1,
                        '2': 0.1,
                    },
                    '3': {
                        '0': 0.0,
                        '1': 0.0,
                        '2': 0.8,
                    }
                }
            },
        ]
        self.fake_schema_mapper = (
            schemamapping
            .SchemaMapper
            .from_taxonomy_and_damage_state_conversion_data(
                tax_schema_mapping_data, ds_schema_mapping_data
            )
        )
        self.fake_loss_provider = (
            testimplementations
            .AlwaysOneDollarPerTransitionLossProvider()
        )

    def test_with_schema_mapping(self):
        """
        Runs a test case with schema mapping.
        """
        result_exposure = gpdexposure.update_exposure_transitions_and_losses(
            exposure=self.old_exposure,
            source_schema='SCHEMA1',
            schema_mapper=self.fake_schema_mapper,
            intensity_provider=self.fake_intensity_provider,
            fragility_provider=self.fake_fragility_provider2,
            loss_provider=self.fake_loss_provider
        )
        self.assertEqual(1, len(result_exposure))
        expo = pandas.DataFrame(result_exposure.iloc[0].expo)

        self.assertEqual(4, len(expo))

        # This here was the mapping only
        self.assertEqual(24, get_buildings(expo, 'TAX', 'D0'))
        self.assertBetween(139.19, get_buildings(expo, 'TAX', 'D1'), 140.01)
        self.assertBetween(140.79, get_buildings(expo, 'TAX', 'D2'), 140.81)
        self.assertEqual(96, get_buildings(expo, 'TAX', 'D3'))

    def test_without_schema_mapping(self):
        """
        Runs a test case without schema mapping.
        """
        result_exposure = gpdexposure.update_exposure_transitions_and_losses(
            exposure=self.old_exposure,
            source_schema='SCHEMA1',
            schema_mapper=self.fake_schema_mapper,
            intensity_provider=self.fake_intensity_provider,
            fragility_provider=self.fake_fragility_provider,
            loss_provider=self.fake_loss_provider
        )
        self.assertEqual(1, len(result_exposure))
        expo = pandas.DataFrame(result_exposure.iloc[0].expo)

        self.assertEqual(6, len(expo))

        self.assertBetween(37.49, get_buildings(expo, 'TAX1', 'D0'), 37.51)
        self.assertBetween(112.49, get_buildings(expo, 'TAX1', 'D1'), 112.51)
        self.assertBetween(49.99, get_buildings(expo, 'TAX1', 'D2'), 50.01)

        self.assertBetween(14.99, get_buildings(expo, 'TAX2', 'D0'), 15.01)
        self.assertBetween(104.99, get_buildings(expo, 'TAX2', 'D1'), 105.01)
        self.assertBetween(79.99, get_buildings(expo, 'TAX2', 'D2'), 80.01)

    def assertBetween(self, lower, x, upper):
        """
        Test that a number is between two others.
        """
        self.assertLess(lower, x)
        self.assertLess(x, upper)


def get_buildings(expo, tax, ds):
    """
    Helper method to get the buildings value.
    """
    expo_tax = expo[expo.Taxonomy == tax]
    expo_ds = expo_tax[expo_tax.Damage == ds]
    return expo_ds.Buildings.iloc[0]


class MakeFakeFunction:
    """
    In the test_performace_optimization.py we used
    a nested function.
    But since gpdexposure works with multiprocessing,
    we need to serialize the functions used there,
    so we use a class instead of a nested function.
    """
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def __call__(self, intensity):
        return self.mean


if __name__ == '__main__':
    unittest.main()
