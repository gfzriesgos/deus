#!/usr/bin/env python3

# Copyright © 2021-2022 Helmholtz Centre Potsdam GFZ German Research Centre for
# Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Testcases for the schema mappings.
"""

import glob
import json
import os
import unittest

import gpdexposure
import schemamapping
import tellus


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
        self.source_schema = "SCHEMA1"
        self.target_schema = "SCHEMA2"

        self.s1_b1 = "S1_B1"
        self.s1_b2 = "S2_B2"
        self.s2_b1 = "S2_B1"
        self.s2_b2_1 = "S2_B2_1"
        self.s2_b2_2 = "S2_B2_2"

        tax_mapping_data = [
            {
                "source_schema": self.source_schema,
                "target_schema": self.target_schema,
                "source_taxonomies": [self.s1_b1, self.s1_b2],
                "target_taxonomioes": [self.s2_b1, self.s2_b2_1, self.s2_b2_2],
                # the structure is a bit counter intuitive
                # as the first level keys are target_taxonomies
                # but they come from matrixes and this is the
                # default way there
                # same is true for the conversion for damage states
                "conv_matrix": {
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
                    },
                },
            }
        ]

        ds_mapping_data = [
            # all of the damage state mappings are dependent
            # on the source taxonomy and the target taxonomy
            # so we have to give 2x3 Datasets here
            {
                "source_schema": self.source_schema,
                "source_taxonomy": self.s1_b1,
                "target_schema": self.target_schema,
                "target_taxonomy": self.s2_b1,
                "source_damage_states": [0, 1],
                "target_damage_states": [0, 1, 2],
                # for S1_B1 to S2_B1
                # we just set half of the
                # old D1 to new D1 and the other half to D2
                "conv_matrix": {
                    "0": {
                        "0": 1.0,
                        "1": 0.0,
                    },
                    "1": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                    "2": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                },
            },
            {
                "source_schema": self.source_schema,
                "source_taxonomy": self.s1_b1,
                "target_schema": self.target_schema,
                "target_taxonomy": self.s2_b2_1,
                "source_damage_states": [0, 1],
                "target_damage_states": [0, 1, 2],
                # this will not happen, because of the
                # taxonomy conversion
                # so values don't care
                # and we stay with the ones for conversion
                # to S2_B1
                "conv_matrix": {
                    "0": {
                        "0": 1.0,
                        "1": 0.0,
                    },
                    "1": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                    "2": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                },
            },
            {
                "source_schema": self.source_schema,
                "source_taxonomy": self.s1_b1,
                "target_schema": self.target_schema,
                "target_taxonomy": self.s2_b2_2,
                "source_damage_states": [0, 1],
                "target_damage_states": [0, 1, 2],
                # this will not happen, because of the
                # taxonomy conversion
                # so values don't care
                # and we stay with the ones for conversion
                # to S2_B1
                "conv_matrix": {
                    "0": {
                        "0": 1.0,
                        "1": 0.0,
                    },
                    "1": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                    "2": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                },
            },
            {
                "source_schema": self.source_schema,
                "source_taxonomy": self.s1_b2,
                "target_schema": self.target_schema,
                "target_taxonomy": self.s2_b1,
                "source_damage_states": [0, 1],
                "target_damage_states": [0, 1, 2],
                # this will not happen, because of the
                # taxonomy conversion
                # so values don't care
                # and we stay with the ones for conversion
                # for S1_B1 to S2_B1
                "conv_matrix": {
                    "0": {
                        "0": 1.0,
                        "1": 0.0,
                    },
                    "1": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                    "2": {
                        "0": 0.0,
                        "1": 0.5,
                    },
                },
            },
            {
                "source_schema": self.source_schema,
                "source_taxonomy": self.s1_b2,
                "target_schema": self.target_schema,
                "target_taxonomy": self.s2_b2_1,
                "source_damage_states": [0, 1],
                "target_damage_states": [0, 1, 2],
                # here the conversion will happen again
                # and here we put 75 % in D1, and only 25% in D2
                "conv_matrix": {
                    "0": {
                        "0": 1.0,
                        "1": 0.0,
                    },
                    "1": {
                        "0": 0.0,
                        "1": 0.75,
                    },
                    "2": {
                        "0": 0.0,
                        "1": 0.25,
                    },
                },
            },
            {
                "source_schema": self.source_schema,
                "source_taxonomy": self.s1_b2,
                "target_schema": self.target_schema,
                "target_taxonomy": self.s2_b2_2,
                "source_damage_states": [0, 1],
                "target_damage_states": [0, 1, 2],
                # here the conversion will happen again
                # and here we put 25 % in D1, and 75% in D2
                "conv_matrix": {
                    "0": {
                        "0": 1.0,
                        "1": 0.0,
                    },
                    "1": {
                        "0": 0.0,
                        "1": 0.25,
                    },
                    "2": {
                        "0": 0.0,
                        "1": 0.75,
                    },
                },
            },
        ]

        # fmt: off
        self.schema_mapper = \
            schemamapping. \
            SchemaMapper. \
            from_taxonomy_and_damage_state_conversion_data(
                tax_mapping_data,
                ds_mapping_data
            )
        # fmt: on

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

        self.assertEqual(single_mapping_result.schema, self.source_schema)
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

        self.assertEqual(single_mapping_result.schema, self.target_schema)
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
            x for x in mapping_results if x.damage_state == 1
        ][0]

        d2_mapping_result = [
            x for x in mapping_results if x.damage_state == 2
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
            x
            for x in mapping_results
            if x.damage_state == 1 and x.taxonomy == self.s2_b2_1
        ][0]

        b2_1_d2_mapping_result = [
            x
            for x in mapping_results
            if x.damage_state == 2 and x.taxonomy == self.s2_b2_1
        ][0]

        b2_2_d1_mapping_result = [
            x
            for x in mapping_results
            if x.damage_state == 1 and x.taxonomy == self.s2_b2_2
        ][0]

        b2_2_d2_mapping_result = [
            x
            for x in mapping_results
            if x.damage_state == 2 and x.taxonomy == self.s2_b2_2
        ][0]

        self.assertEqual(b2_1_d1_mapping_result.schema, self.target_schema)
        self.assertEqual(b2_1_d1_mapping_result.taxonomy, self.s2_b2_1)
        self.assertEqual(b2_1_d1_mapping_result.damage_state, 1)
        self.assertLess(18.749, b2_1_d1_mapping_result.n_buildings)
        self.assertLess(b2_1_d1_mapping_result.n_buildings, 18.751)

        self.assertEqual(b2_1_d2_mapping_result.schema, self.target_schema)
        self.assertEqual(b2_1_d2_mapping_result.taxonomy, self.s2_b2_1)
        self.assertEqual(b2_1_d2_mapping_result.damage_state, 2)
        self.assertLess(6.249, b2_1_d2_mapping_result.n_buildings)
        self.assertLess(b2_1_d2_mapping_result.n_buildings, 6.251)

        self.assertEqual(b2_2_d1_mapping_result.schema, self.target_schema)
        self.assertEqual(b2_2_d1_mapping_result.taxonomy, self.s2_b2_2)
        self.assertEqual(b2_2_d1_mapping_result.damage_state, 1)
        self.assertLess(18.749, b2_2_d1_mapping_result.n_buildings)
        self.assertLess(b2_2_d1_mapping_result.n_buildings, 18.751)

        self.assertEqual(b2_2_d2_mapping_result.schema, self.target_schema)
        self.assertEqual(b2_2_d2_mapping_result.taxonomy, self.s2_b2_2)
        self.assertEqual(b2_2_d2_mapping_result.damage_state, 2)
        self.assertLess(56.249, b2_2_d2_mapping_result.n_buildings)
        self.assertLess(b2_2_d2_mapping_result.n_buildings, 56.251)


class TestSchemaMappingCoverage(unittest.TestCase):
    """Test the coverage of the schema mapping files."""

    def test_taxonomies_sara_to_medina(self):
        """
        Test the coverage of the sara to medina taxonomy conversion.

        The files to map the taxonomies from sara to medina should
        cover the same source taxonmies as the conversion from
        sara to suppasri.
        """
        this_file = __file__
        this_dir = os.path.dirname(this_file)
        tax_mapping_dir = os.path.join(this_dir, "schema_mapping_data_tax")

        tax_mapping_files = glob.glob(os.path.join(tax_mapping_dir, "*.json"))
        tax_mapping_data = []

        for filename in tax_mapping_files:
            with open(filename) as infile:
                tax_mapping_data.append(json.load(infile))

        sara_to_suppasri = [
            x["source_taxonomies"]
            for x in tax_mapping_data
            if x["source_schema"] == "SARA_v1.0"
            and x["target_schema"] == "SUPPASRI2013_v2.0"
        ][0]

        sara_to_medina = [
            x["source_taxonomies"]
            for x in tax_mapping_data
            if x["source_schema"] == "SARA_v1.0"
            and x["target_schema"] == "Medina_2019"
        ][0]

        # We start testing some (to be sure our lists are not empty)
        self.assertIn("MCF-DNO-H1-3", sara_to_suppasri)
        self.assertIn("CR-LWAL-DNO-H1-3", sara_to_suppasri)

        self.assertIn("MCF-DNO-H1-3", sara_to_medina)

        # And then we want to be sure that we cover all the taxonmies
        # that we also handle in the conversion to suppasri.
        # However, for RIESGOS we decided not to use some of
        # the older taxonomies anymore (they belong to sara, but
        # should not be used in our exposure models anymore).
        tax_to_ignore_for_sara_to_medina = set(
            [
                "CR-LFINF-DUC-H4-7",
                "CR-LFLS-DNO-H1-3",
                "CR-LFLS-DUC-H1-3",
                "CR-LFLS-DUC-H4-7",
                "CR-LFM-DNO-H1-3",
                "CR-LFM-DNO-H4-7",
                "CR-LFM-DNO-SOS-H1-3",
                "CR-LFM-DNO-SOS-H4-7",
                "CR-LFM-DUC-H1-3",
                "CR-LFM-DUC-H4-7",
                "S-LFM-H4-7",
            ]
        )
        for taxonomy in sara_to_suppasri:
            if taxonomy not in tax_to_ignore_for_sara_to_medina:
                self.assertIn(taxonomy, sara_to_medina)

    def test_damage_states_sara_to_medina(self):
        """
        Test the coverage of the sara to medina damage state conversion.

        The files to map the damage states should cover all the
        taxonomies that the taxonomy conversion file handles.
        """
        this_file = __file__
        this_dir = os.path.dirname(this_file)
        tax_mapping_dir = os.path.join(this_dir, "schema_mapping_data_tax")

        tax_mapping_files = glob.glob(os.path.join(tax_mapping_dir, "*.json"))
        tax_mapping_data = []

        for filename in tax_mapping_files:
            with open(filename) as infile:
                tax_mapping_data.append(json.load(infile))

        tax_covered_taxonomies = [
            x["source_taxonomies"]
            for x in tax_mapping_data
            if x["source_schema"] == "SARA_v1.0"
            and x["target_schema"] == "Medina_2019"
        ][0]

        ds_mapping_dir = os.path.join(this_dir, "schema_mapping_data_ds")
        ds_mapping_files = glob.glob(os.path.join(ds_mapping_dir, "*.json"))
        ds_mapping_data = []

        for filename in ds_mapping_files:
            with open(filename) as infile:
                ds_mapping_data.append(json.load(infile))

        ds_covered_taxonomies = set(
            [
                x["source_taxonomy"]
                for x in ds_mapping_data
                if x["source_schema"] == "SARA_v1.0"
                and x["target_schema"] == "Medina_2019"
            ]
        )

        self.assertIn("CR-PC-LWAL-H1-3", tax_covered_taxonomies)
        self.assertIn("CR-PC-LWAL-H1-3", ds_covered_taxonomies)

        for taxonomy in tax_covered_taxonomies:
            self.assertIn(taxonomy, ds_covered_taxonomies)


class TestFullSchemaMapping(unittest.TestCase):
    """Run the full schema mapping for exposure files."""

    def setUp(self):
        """Set up the tests with a real world schema mapping."""
        current_dir = os.path.dirname(__file__)
        self.schema_mapper = tellus.create_schema_mapper(current_dir)

        path_expo_input = os.path.join(
            current_dir, "testinputs", "expo_valp_bayes_after_1_deus_run.json"
        )
        self.old_exposure = gpdexposure.read_exposure(path_expo_input)

    def test_sara_to_medina_in_valparaiso(self):
        """
        Test the mapping from a sara model to medina.

        As we had trouble several times to map the sara model to
        medina we want to run all of the code in our test.
        """
        for expo in self.old_exposure.expo:
            expo = gpdexposure.expo_from_series_to_dict(expo)
            mapped_exposure = gpdexposure.map_exposure(
                expo=expo,
                source_schema="SARA_v1.0",
                target_schema="Medina_2019",
                schema_mapper=self.schema_mapper,
            )
            sum_all_buildings_in = sum([x.buildings for x in expo.values()])
            sum_all_buildings_out = sum(
                [x.buildings for x in mapped_exposure.values()]
            )
            self.assertAlmostEqual(sum_all_buildings_in, sum_all_buildings_out)

    def test_sara_to_suppasri_in_valparaiso(self):
        """
        Test the mapping from a sara model to suppasri.

        This is also meant as a test for the other schema mapping
        test to medina.
        """
        for expo in self.old_exposure.expo:
            expo = gpdexposure.expo_from_series_to_dict(expo)
            mapped_exposure = gpdexposure.map_exposure(
                expo=expo,
                source_schema="SARA_v1.0",
                target_schema="SUPPASRI2013_v2.0",
                schema_mapper=self.schema_mapper,
            )
            sum_all_buildings_in = sum([x.buildings for x in expo.values()])
            sum_all_buildings_out = sum(
                [x.buildings for x in mapped_exposure.values()]
            )
            self.assertAlmostEqual(sum_all_buildings_in, sum_all_buildings_out)


if __name__ == "__main__":
    unittest.main()
