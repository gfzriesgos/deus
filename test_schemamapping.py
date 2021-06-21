#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright (C) 2019-2021
# - Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
# - Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
# - Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
# - Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)
#
# - Helmholtz Centre Potsdam - GFZ German Research Centre for
#   Geosciences (GFZ, https://www.gfz-potsdam.de) 
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)
#
# Licensed under the Apache License, Version 2.0.
#
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at:
# https://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the Licence for the specific language governing
# permissions and limitations under the Licence.

"""
Testcases for the schema mappings.
"""

import glob
import os
import unittest

import geopandas as gpd
import pandas as pd

from shapely import wkt

import schemamapping


class TestSchemaMapping(unittest.TestCase):
    """
    This is a test for supporting the changing
    the way the schema mapping works.

    In older versions I was in the opinion
    that all the schema mapping
    is done via the large number of
    schema mapping files all going down
    to the level of damage states.

    I was told by Max that this is not the case.
    All this "old" mapping files are just for
    the damage state conversion and not intended
    to work for the taxonomy conversion.

    (And I understand this because maintaining
    the conversion over a lot of files can't be
    handled in the long term.
    Fixing one file for the damage states
    alone - even it if is specific to
    the source and the target taxonomy - can
    be handled way better.

    So here we want to write the classes for
    the *real new* way to do the schema mapping,
    before we replace all the old classes for the
    old way.
    """

    def setUp(self):
        """
        Set up a setting with some base schema
        mapping data.
        """
        self.source_schema = 'SCHEMA1'
        self.target_schema = 'SCHEMA2'

        self.s1_b1 = 'S1_B1'
        self.s1_b2 = 'S2_B2'
        self.s2_b1 = 'S2_B1'
        self.s2_b2_1 = 'S2_B2_1'
        self.s2_b2_2 = 'S2_B2_2'

        tax_mapping_data = [
            {
                'source_schema': self.source_schema,
                'target_schema': self.target_schema,
                'source_taxonomies': [self.s1_b1, self.s1_b2],
                'target_taxonomioes': [self.s2_b1, self.s2_b2_1, self.s2_b2_2],
                # the structure is a bit counter intuitive
                # as the first level keys are target_taxonomies
                # but they come from matrixes and this is the
                # default way there
                # same is true for the conversion for damage states
                'conv_matrix': {
                    # all of our S1_B1 go to s2_b2_1
                    self.s1_b1: {
                        self.s2_b1: 1.0,
                        self.s2_b2_1: 0.0,
                        self.s2_b2_2: 0.0,
                    },
                    # and all our S1_B2 should be splitted
                    # into S2_B2_1 and S2_B2_2
                    self.s1_b2: {
                        self.s2_b1: 0.0,
                        self.s2_b2_1: 0.25,
                        self.s2_b2_2: 0.75,
                    }
                }
            }
        ]

        ds_mapping_data = [
            # all of the damage state mappings are dependent
            # on the source taxonomy and the target taxonomy
            # so we have to give 2x3 Datasets here
            {
                'source_schema': self.source_schema,
                'source_taxonomy': self.s1_b1,
                'target_schema': self.target_schema,
                'target_taxonomy': self.s2_b1,
                'source_damage_states': [0, 1],
                'target_damage_states': [0, 1, 2],
                # for S1_B1 to S2_B1
                # we just set half of the
                # old D1 to new D1 and the other half to D2
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                },
            },
            {
                'source_schema': self.source_schema,
                'source_taxonomy': self.s1_b1,
                'target_schema': self.target_schema,
                'target_taxonomy': self.s2_b2_1,
                'source_damage_states': [0, 1],
                'target_damage_states': [0, 1, 2],
                # this will not happen, because of the
                # taxonomy conversion
                # so values don't care
                # and we stay with the ones for conversion
                # to S2_B1
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                },
            },
            {
                'source_schema': self.source_schema,
                'source_taxonomy': self.s1_b1,
                'target_schema': self.target_schema,
                'target_taxonomy': self.s2_b2_2,
                'source_damage_states': [0, 1],
                'target_damage_states': [0, 1, 2],
                # this will not happen, because of the
                # taxonomy conversion
                # so values don't care
                # and we stay with the ones for conversion
                # to S2_B1
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                },
            },
            {
                'source_schema': self.source_schema,
                'source_taxonomy': self.s1_b2,
                'target_schema': self.target_schema,
                'target_taxonomy': self.s2_b1,
                'source_damage_states': [0, 1],
                'target_damage_states': [0, 1, 2],
                # this will not happen, because of the
                # taxonomy conversion
                # so values don't care
                # and we stay with the ones for conversion
                # for S1_B1 to S2_B1
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.5,
                    },
                },
            },
            {
                'source_schema': self.source_schema,
                'source_taxonomy': self.s1_b2,
                'target_schema': self.target_schema,
                'target_taxonomy': self.s2_b2_1,
                'source_damage_states': [0, 1],
                'target_damage_states': [0, 1, 2],
                # here the conversion will happen again
                # and here we put 75 % in D1, and only 25% in D2
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.75,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.25,
                    },
                },
            },
            {
                'source_schema': self.source_schema,
                'source_taxonomy': self.s1_b2,
                'target_schema': self.target_schema,
                'target_taxonomy': self.s2_b2_2,
                'source_damage_states': [0, 1],
                'target_damage_states': [0, 1, 2],
                # here the conversion will happen again
                # and here we put 25 % in D1, and 75% in D2
                'conv_matrix': {
                    '0': {
                        '0': 1.0,
                        '1': 0.0,
                    },
                    '1': {
                        '0': 0.0,
                        '1': 0.25,
                    },
                    '2': {
                        '0': 0.0,
                        '1': 0.75,
                    },
                },
            },
        ]

        self.schema_mapper = (
            schemamapping
            .SchemaMapper
            .from_taxonomy_and_damage_state_conversion_data(
                tax_mapping_data,
                ds_mapping_data
            )
        )

    def test_same_input_and_output_schema(self):
        """
        Here we just use the very same target schema
        also as input schema.
        """

        mapping_results = self.schema_mapper.map_schema(
            source_schema=self.source_schema,
            source_taxonomy=self.s1_b1,
            source_damage_state=0,
            target_schema=self.source_schema,
            n_buildings=100,
        )

        self.assertEqual(len(mapping_results), 1)

        single_mapping_result = mapping_results[0]

        self.assertEqual(
            single_mapping_result.schema,
            self.source_schema
        )
        self.assertEqual(single_mapping_result.taxonomy, self.s1_b1)
        self.assertEqual(single_mapping_result.damage_state, 0)
        self.assertLess(99.999, single_mapping_result.n_buildings)
        self.assertLess(single_mapping_result.n_buildings, 100.001)

    def test_mapping_s1_b1_to_s2_b1_for_d0(self):
        """
        This is the test for the conversion of S1_B1 to
        S2_B1.
        Only D0 will be covered, so that we can be sure
        that we only have one result (as the S1_B1 to
        S2_B1 mapping is 1:1 and the mapping of D0 is 1:1
        too).
        """

        mapping_results = self.schema_mapper.map_schema(
            source_schema=self.source_schema,
            source_taxonomy=self.s1_b1,
            source_damage_state=0,
            target_schema=self.target_schema,
            n_buildings=100,
        )

        self.assertEqual(len(mapping_results), 1)

        single_mapping_result = mapping_results[0]

        self.assertEqual(
            single_mapping_result.schema,
            self.target_schema
        )
        self.assertEqual(single_mapping_result.taxonomy, self.s2_b1)
        self.assertEqual(single_mapping_result.damage_state, 0)
        self.assertLess(99.999, single_mapping_result.n_buildings)
        self.assertLess(single_mapping_result.n_buildings, 100.001)

    def test_mapping_s1_b1_to_s2_b1_for_d1(self):
        """
        This is mostly the same as the
        test_mapping_s1_b1_to_s2_b1_for_d0 case,
        but since we use D1 as source damage state here,
        we will split the builings into the target damage states
        D1 and D2.
        Every case will contain 50%.
        """

        mapping_results = self.schema_mapper.map_schema(
            source_schema=self.source_schema,
            source_taxonomy=self.s1_b1,
            source_damage_state=1,
            target_schema=self.target_schema,
            n_buildings=100,
        )

        self.assertEqual(len(mapping_results), 2)

        d1_mapping_result = [
            x for x in mapping_results
            if x.damage_state == 1
        ][0]

        d2_mapping_result = [
            x for x in mapping_results
            if x.damage_state == 2
        ][0]

        self.assertEqual(d1_mapping_result.schema, self.target_schema)
        self.assertEqual(d1_mapping_result.taxonomy, self.s2_b1)
        self.assertEqual(d1_mapping_result.damage_state, 1)
        self.assertLess(49.999, d1_mapping_result.n_buildings)
        self.assertLess(d1_mapping_result.n_buildings, 50.001)

        self.assertEqual(d2_mapping_result.schema, self.target_schema)
        self.assertEqual(d2_mapping_result.taxonomy, self.s2_b1)
        self.assertEqual(d2_mapping_result.damage_state, 2)
        self.assertLess(49.999, d2_mapping_result.n_buildings)
        self.assertLess(d2_mapping_result.n_buildings, 50.001)

    def test_mapping_s1_b2_for_d1(self):
        """
        This will do the mapping for
        s1_b2 into the target schema.
        It will split into two different taxonomies
        and both will split into two different damage states
        as well (using different ratios).
        """
        mapping_results = self.schema_mapper.map_schema(
            source_schema=self.source_schema,
            source_taxonomy=self.s1_b2,
            source_damage_state=1,
            target_schema=self.target_schema,
            n_buildings=100,
        )

        self.assertEqual(len(mapping_results), 4)

        b2_1_d1_mapping_result = [
            x for x in mapping_results
            if x.damage_state == 1
            and x.taxonomy == self.s2_b2_1
        ][0]

        b2_1_d2_mapping_result = [
            x for x in mapping_results
            if x.damage_state == 2
            and x.taxonomy == self.s2_b2_1
        ][0]

        b2_2_d1_mapping_result = [
            x for x in mapping_results
            if x.damage_state == 1
            and x.taxonomy == self.s2_b2_2
        ][0]

        b2_2_d2_mapping_result = [
            x for x in mapping_results
            if x.damage_state == 2
            and x.taxonomy == self.s2_b2_2
        ][0]

        self.assertEqual(
            b2_1_d1_mapping_result.schema,
            self.target_schema
        )
        self.assertEqual(b2_1_d1_mapping_result.taxonomy, self.s2_b2_1)
        self.assertEqual(b2_1_d1_mapping_result.damage_state, 1)
        self.assertLess(18.749, b2_1_d1_mapping_result.n_buildings)
        self.assertLess(b2_1_d1_mapping_result.n_buildings, 18.751)

        self.assertEqual(
            b2_1_d2_mapping_result.schema,
            self.target_schema
        )
        self.assertEqual(b2_1_d2_mapping_result.taxonomy, self.s2_b2_1)
        self.assertEqual(b2_1_d2_mapping_result.damage_state, 2)
        self.assertLess(6.249, b2_1_d2_mapping_result.n_buildings)
        self.assertLess(b2_1_d2_mapping_result.n_buildings, 6.251)

        self.assertEqual(
            b2_2_d1_mapping_result.schema,
            self.target_schema
        )
        self.assertEqual(b2_2_d1_mapping_result.taxonomy, self.s2_b2_2)
        self.assertEqual(b2_2_d1_mapping_result.damage_state, 1)
        self.assertLess(18.749, b2_2_d1_mapping_result.n_buildings)
        self.assertLess(b2_2_d1_mapping_result.n_buildings, 18.751)

        self.assertEqual(
            b2_2_d2_mapping_result.schema,
            self.target_schema
        )
        self.assertEqual(b2_2_d2_mapping_result.taxonomy, self.s2_b2_2)
        self.assertEqual(b2_2_d2_mapping_result.damage_state, 2)
        self.assertLess(56.249, b2_2_d2_mapping_result.n_buildings)
        self.assertLess(b2_2_d2_mapping_result.n_buildings, 56.251)


if __name__ == '__main__':
    unittest.main()
