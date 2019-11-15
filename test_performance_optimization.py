#!/usr/bin/env python3

"""
This is an additional test, that all of your
code works fine before and after the performance
optimization (most importantly for the change of
the taxonomy data bag handling).
"""

import unittest

import pandas
import shapely.wkt

import testimplementations

import exposure
import fragility
import schemamapping


class TestExposureDamageStateUpdate(unittest.TestCase):
    """
    This is a test class for working with one
    exposure cell and updateting the damage states.
    """

    def setUp(self):
        # lets say we have 400 buildings
        # TAX1 D0 with 100
        # TAX1 D1 with 100
        # TAX2 D0 with 100
        # TAX2 D1 with 100
        expo = pandas.DataFrame({
            'id': ['id-1'] * 4,
            'Region': [None] * 4,
            'Dwellings': [None] * 4,
            'Repl-cost-USD-bdg': [None] * 4,
            'Population': [None] * 4,
            'name': [None] * 4,
            'Buildings': [100.0] * 4,
            'Taxonomy': ['TAX1', 'TAX1', 'TAX2', 'TAX2'],
            'Damage': ['D0', 'D1', 'D0', 'D1'],
        })

        series = pandas.Series({
            'gid': '001',
            'name': 'Cell1',
            'geometry': shapely.wkt.loads('POINT(52 15)'),
            'expo': expo
        })
        self.exposure_cell = exposure.ExposureCell.from_series(
            schema='SCHEMA1',
            series=series
        )
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

        def make_fake_function(mean, stddev):
            def get_prop(intensity):
                return mean
            return get_prop

        self.fake_fragility_provider = fragility.Fragility(
            fragility_data
        ).to_fragility_provider_with_specified_fragility_function(
            make_fake_function
        )
        # and another one for the schema mapping too
        self.fake_fragility_provider2 = fragility.Fragility(
            fragility_data2
        ).to_fragility_provider_with_specified_fragility_function(
            make_fake_function
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

    def test_fake_intensity_provider(self):
        """
        Just a test to make sure that our mocking is ok.
        """
        intensities, units = self.fake_intensity_provider.get_nearest(
            lon=51, lat=15
        )
        self.assertEqual(
            intensities,
            {'INTENSITY': 1}
        )
        self.assertEqual(
            units,
            {'INTENSITY': 'unitless'}
        )

    def test_with_schema_mapping(self):
        """
        Tests the schema mapping with the taxonomy bag
        implementation.
        """
        mapped_cell = self.exposure_cell.map_schema(
            'SCHEMA2',
            self.fake_schema_mapper
        )

        taxonomies = mapped_cell.taxonomies

        # so we do just the conversion here
        #              TAX    D0    D1    D2    D3
        # 100 Tax1 D0 ->     100     0     0     0
        # 100 Tax1 D1 ->       0    50    30    20
        # 100 Tax2 D0 ->     100     0     0     0
        # 100 Tax2 D1 ->       0    90    10     0
        #
        #                    200   140    40    20

        self.assertEqual(4, len(taxonomies))

        tax_d0 = [
            x for x in taxonomies
            if x['damage_state'] == 0
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertEqual(200, tax_d0['n_buildings'])

        tax_d1 = [
            x for x in taxonomies
            if x['damage_state'] == 1
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertEqual(140, tax_d1['n_buildings'])

        tax_d2 = [
            x for x in taxonomies
            if x['damage_state'] == 2
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertEqual(40, tax_d2['n_buildings'])

        tax_d3 = [
            x for x in taxonomies
            if x['damage_state'] == 3
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertEqual(20, tax_d3['n_buildings'])

    def test_without_schema_mapping(self):
        """
        Tests the update process without
        a schema mapping.
        """
        updated_cell, transitions = self.exposure_cell.update(
            self.fake_intensity_provider,
            self.fake_fragility_provider
        )

        # now it is the question what do we expect?
        # we start with 100 TAX1 D0
        # the first ds that we check is TAX1 D2
        #
        # from our take fragility function we know
        # that 25% of our 100 buildings go into D2
        # --> 25 TAX1 D2
        # now we still have 75 TAX1 D0
        # and we test TAX1 D1
        # we now that 50% of them will be in D1
        # --> 37.5 are now in TAX D1
        # --> Rest (37.5) stay in D0
        #
        # now we have 100 buildings in TAX1 D1
        # the first ds to test here is TAX1 D2
        # so 25 Buildings will be there in TAX1 D2
        # coming from TAX1 D1
        #
        # so overall we have 25+25 = 50 in TAX1 D2
        #
        # the rest here stays in TAX1 D1
        # so 75+37.5 = 112.5 in Tax D1 overall

        taxonomies = updated_cell.taxonomies

        tax1_d0 = [
            x for x in taxonomies
            if x['damage_state'] == 0
            and x['taxonomy'] == 'TAX1'
        ][0]

        self.assertLess(37.49, tax1_d0['n_buildings'])
        self.assertLess(tax1_d0['n_buildings'], 37.51)

        tax1_d1 = [
            x for x in taxonomies
            if x['damage_state'] == 1
            and x['taxonomy'] == 'TAX1'
        ][0]

        self.assertLess(112.49, tax1_d1['n_buildings'])
        self.assertLess(tax1_d1['n_buildings'], 112.51)

        tax1_d2 = [
            x for x in taxonomies
            if x['damage_state'] == 2
            and x['taxonomy'] == 'TAX1'
        ][0]

        self.assertLess(49.99, tax1_d2['n_buildings'])
        self.assertLess(tax1_d2['n_buildings'], 50.01)

        # so we do the very same stuff for tax2
        # from 100 in D0 we will get 40 in D2
        # 60 remaining for D0/D1
        # of this 60 we will have 45 in D1
        # and 15 in D0
        #
        # we also have 100 in D1, so we will have
        # 40 in D2 and 60 remaning in D1
        #
        # D0 = 15
        # D1 = 60 + 45 = 105
        # D2 = 40 + 40 = 80

        tax2_d0 = [
            x for x in taxonomies
            if x['damage_state'] == 0
            and x['taxonomy'] == 'TAX2'
        ][0]

        self.assertLess(14.99, tax2_d0['n_buildings'])
        self.assertLess(tax2_d0['n_buildings'], 15.01)

        tax2_d1 = [
            x for x in taxonomies
            if x['damage_state'] == 1
            and x['taxonomy'] == 'TAX2'
        ][0]

        self.assertLess(104.99, tax2_d1['n_buildings'])
        self.assertLess(tax2_d1['n_buildings'], 105.01)

        tax2_d2 = [
            x for x in taxonomies
            if x['damage_state'] == 2
            and x['taxonomy'] == 'TAX2'
        ][0]

        self.assertLess(79.99, tax2_d2['n_buildings'])
        self.assertLess(tax2_d2['n_buildings'], 80.01)

        self.assertEqual(6, len(taxonomies))

    def test_chain(self):
        """
        Tests a chain of update, mapping and update.
        We can reuse the first update values.
        """

        updated_cell, transitions = self.exposure_cell.update(
            self.fake_intensity_provider,
            self.fake_fragility_provider
        )

        # the mapping
        #              Tax    D0     D1      D2     D3
        # 37.5 Tax1 D0      37.5   0.00    0.00    0.0
        # 112.5 Tax1 D1      0.0  56.25   33.75   22.5
        # 50 Tax1 D2         0.0  10.00   15.00   25.0
        # 15 Tax1 D0        15.0   0.00    0.00    0.0
        # 105 Tax1 D1        0.0  94.50   10.50    0.0
        # 80 Tax D2          0.0   8.00    8.00   64.0
        #
        #                   52.5  168.75  67.25  111.5

        mapped_cell = updated_cell.map_schema(
            'SCHEMA2',
            self.fake_schema_mapper
        )

        updated_cell2, transitions = mapped_cell.update(
            self.fake_intensity_provider,
            self.fake_fragility_provider2
        )

        taxonomies = updated_cell2.taxonomies

        self.assertEqual(4, len(taxonomies))

        tax_d0 = [
            x for x in taxonomies
            if x['damage_state'] == 0
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertLess(6.29, tax_d0['n_buildings'])
        self.assertLess(tax_d0['n_buildings'], 6.31)

        tax_d1 = [
            x for x in taxonomies
            if x['damage_state'] == 1
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertLess(99.8, tax_d1['n_buildings'])
        self.assertLess(tax_d1['n_buildings'], 99.91)

        tax_d2 = [
            x for x in taxonomies
            if x['damage_state'] == 2
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertEqual(124.6, tax_d2['n_buildings'])

        tax_d3 = [
            x for x in taxonomies
            if x['damage_state'] == 3
            and x['taxonomy'] == 'TAX'
        ][0]

        self.assertEqual(169.2, tax_d3['n_buildings'])


if __name__ == '__main__':
    unittest.main()
