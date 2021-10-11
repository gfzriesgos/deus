#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

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
            'Buildings': [100.0, 100.0, 100.0, 100.0],
            'Population': [20.0, 10.0, 20.0, 10.0],
            'Repl-cost-USD-bdg': [50000, 45000, 60000, 59000]
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
                        # TAX1 D0 goes to 100% into TAX D0
                        '0': 1.0,
                        '1': 0.0,
                        '2': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        # TAX1 D1 goes to 50% into TAX D1
                        '1': 0.5,
                        '2': 0.2,
                    },
                    '2': {
                        '0': 0.0,
                        # TAX1 D1 goes to 30% into TAX D2
                        '1': 0.3,
                        '2': 0.3,
                    },
                    '3': {
                        '0': 0.0,
                        # TAX1 D1 goes to 20% into TAX D3
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
        # (but with applying the damage computation)
        self.assertEqual(24, get_buildings(expo, 'TAX', 'D0'))
        self.assertBetween(139.19, get_buildings(expo, 'TAX', 'D1'), 140.01)
        self.assertBetween(140.79, get_buildings(expo, 'TAX', 'D2'), 140.81)
        self.assertEqual(96, get_buildings(expo, 'TAX', 'D3'))

        # Population follows the same algorithm as the number of buildings
        self.assertBetween(4.79, get_population(expo, 'TAX', 'D0'), 4.81)
        self.assertBetween(21.11, get_population(expo, 'TAX', 'D1'), 21.13)
        self.assertBetween(20.47, get_population(expo, 'TAX', 'D2'), 20.49)
        self.assertBetween(13.5, get_population(expo, 'TAX', 'D3'), 13.7)

        # The replacement costs don't follow the route of building handling.
        #
        # First we calculate the total replacement costs per class
        #
        # totalRepl('TAX1', 'D0') = replBdg('TAX1', 'D0') * nBdg('TAX1', 'D0')
        #                         = 50_000 * 100
        #                         = 5_000_000
        # totalRepl('TAX1', 'D1') = 4_500_000
        # totalRepl('TAX2', 'D0') = 6_000_000
        # totalRepl('TAX2', 'D1') = 5_900_000
        #
        # Then we map the total replacement costs to the other schemas:
        #
        # totalRepl('TAX', 'D0') = (
        #                            totalRepl('TAX1', 'D0') *
        #                              p('TAX1', 'D0', 'TAX', 'D0') +
        #                            totalRepl('TAX2', 'D0') *
        #                              p('TAX2', 'D0', 'TAX', 'D0')
        #                          )
        #                        = 5_000_000 * 1 + 6_000_000 * 1
        # totalRepl('TAX', 'D0') = 11_000_000
        # totalRepl('TAX', 'D1') = (
        #                            totalRepl('TAX1', 'D1') *
        #                              p('TAX1', 'D1', 'TAX', 'D1') +
        #                            totalRepl('TAX2', 'D1') *
        #                              p('TAX2', 'D1', 'TAX', 'D1')
        #                          )
        #                        = 4_500_000 * 0.5 + 5_900_000 * 0.9
        #                        = 7_560_000
        # totalRepl('TAX', 'D2') = (
        #                            totalRepl('TAX1', 'D1') *
        #                              p('TAX1', 'D1', 'TAX', 'D2') +
        #                            totalRepl('TAX2', 'D1') *
        #                              p('TAX2', 'D1', 'TAX', 'D2')
        #                          )
        #                        = 4_500_000 * 0.3 + 5_900_000 * 0.1
        #                        = 1_940_000
        # totalRepl('TAX', 'D3') = totalRepl('TAX1', 'D1') *
        #                          p('TAX1', 'D1', 'TAX', 'D3')
        #                        = 4_500_000 * 0.2
        #                        = 900_000
        #
        # Then we sum those up.
        #
        # totalRepl('TAX') = (
        #                      totalRepl('TAX', 'D0') +
        #                      totalRepl('TAX', 'D1') +
        #                      totalRepl('TAX', 'D2') +
        #                      totalRepl('TAX', 'D3')
        #                    )
        #                  = 21_400_000
        #
        # And last we calculate the replacement cost per building
        #
        # replBdg('TAX') = totalRepl('TAX') / nBdg('TAX')
        # replBdg('TAX') = 21_400_000 / 400
        # replBdg('TAX') = 53_500
        #
        # As we are not going to change the replacement costs on applying
        # the damage, we stay with those values.
        #
        self.assertBetween(
            53_499,
            get_replacement_costs_usd_bdg(expo, 'TAX', 'D0'),
            53_501
        )
        self.assertBetween(
            53_499,
            get_replacement_costs_usd_bdg(expo, 'TAX', 'D1'),
            53_501
        )
        self.assertBetween(
            53_499,
            get_replacement_costs_usd_bdg(expo, 'TAX', 'D2'),
            53_501
        )
        self.assertBetween(
            53_499,
            get_replacement_costs_usd_bdg(expo, 'TAX', 'D3'),
            53_501
        )

        transitions = pandas.DataFrame(result_exposure.iloc[0].transitions)

        self.assertBetween(
            71,
            get_transition_n_bdg(transitions, 'TAX', 0, 1),
            73
        )
        self.assertBetween(
            63,
            get_transition_n_bdg(transitions, 'TAX', 0, 2),
            65
        )
        self.assertBetween(
            39,
            get_transition_n_bdg(transitions, 'TAX', 0, 3),
            41
        )
        self.assertBetween(
            44.7,
            get_transition_n_bdg(transitions, 'TAX', 1, 2),
            44.9
        )
        self.assertBetween(
            27.9,
            get_transition_n_bdg(transitions, 'TAX', 1, 3),
            28.1
        )
        self.assertBetween(
            7.9,
            get_transition_n_bdg(transitions, 'TAX', 2, 3),
            8.1
        )

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

        # Normally the replacement costs per building would stay the very same
        # as the input values (as all of those are only taxonomy specific and
        # oriented on the replacement costs of D0).
        # However, as there is the danger, that the replacement costs are
        # different over the damage states (having not completely reliable
        # input), we are going to compute weighted means before applying
        # the damage state conversion.
        #
        # Again we go over the total replacement costs:
        # totalRepl('TAX1', 'D0') = replBdg('TAX1', 'D0') * nBdg('TAX1', 'D0')
        # ...
        # Then we sum them up
        # totalRepl('TAX1') = totalRepl('TAX1', 'D0') + totalRepl('TAX1', 'D1')
        #
        # And then we calculate the replacement costs per building
        # replBdg('TAX1') = totalRepl('TAX1') / nBdg('TAX1')
        # And those are the very same regardless of the damage state

        self.assertBetween(
            47_499,
            get_replacement_costs_usd_bdg(expo, 'TAX1', 'D0'),
            47_501
        )
        self.assertBetween(
            47_499,
            get_replacement_costs_usd_bdg(expo, 'TAX1', 'D1'),
            47_501
        )
        self.assertBetween(
            47_499,
            get_replacement_costs_usd_bdg(expo, 'TAX1', 'D2'),
            47_501
        )

        self.assertBetween(
            59_499,
            get_replacement_costs_usd_bdg(expo, 'TAX2', 'D0'),
            59_501
        )
        self.assertBetween(
            59_499,
            get_replacement_costs_usd_bdg(expo, 'TAX2', 'D1'),
            59_501
        )
        self.assertBetween(
            59_499,
            get_replacement_costs_usd_bdg(expo, 'TAX2', 'D2'),
            59_501
        )

        transitions = pandas.DataFrame(result_exposure.iloc[0].transitions)

        self.assertBetween(
            37.49,
            get_transition_n_bdg(transitions, 'TAX1', 0, 1),
            37.51
        )
        self.assertBetween(
            24,
            get_transition_n_bdg(transitions, 'TAX1', 0, 2),
            26
        )
        self.assertBetween(
            24,
            get_transition_n_bdg(transitions, 'TAX1', 1, 2),
            26
        )
        self.assertBetween(
            44.9,
            get_transition_n_bdg(transitions, 'TAX2', 0, 1),
            45.1
        )
        self.assertBetween(
            39.9,
            get_transition_n_bdg(transitions, 'TAX2', 0, 2),
            40.1
        )
        self.assertBetween(
            39.9,
            get_transition_n_bdg(transitions, 'TAX2', 1, 2),
            40.1
        )

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


def get_population(expo, tax, ds):
    """Get the population for the tax and the ds."""
    expo_tax = expo[expo.Taxonomy == tax]
    expo_ds = expo_tax[expo_tax.Damage == ds]
    return expo_ds.Population.iloc[0]


def get_replacement_costs_usd_bdg(expo, tax, ds):
    """Get the replacement costs in usd per bdg."""
    expo_tax = expo[expo.Taxonomy == tax]
    expo_ds = expo_tax[expo_tax.Damage == ds]
    return expo_ds['Repl-cost-USD-bdg'].iloc[0]


def get_transition_n_bdg(transitions, tax, from_ds, to_ds):
    """Return the number of buildings in the transition."""
    filter_1 = transitions[transitions.taxonomy == tax]
    filter_2 = filter_1[filter_1.from_damage_state == from_ds]
    filter_3 = filter_2[filter_2.to_damage_state == to_ds]

    return filter_3.n_buildings.iloc[0]


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
