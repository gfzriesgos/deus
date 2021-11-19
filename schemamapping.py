#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
This is a module
for the mapping of the taxonomies.
"""

import collections
import json

import pandas as pd


CacheKey = collections.namedtuple(
    "CacheKey", "source_schema source_taxonomy source_damage_state target_schema"
)

CacheKeyTaxonomy = collections.namedtuple(
    "CacheKeyTaxonomy", "source_schema source_taxonomy target_schema"
)


def convert_dict_to_use_int_keys(d):
    """
    Takes a dict with string keys that
    should be int keys for faster work.

    Returns a generator, so that it can
    be used with dict(convert_dict_to_use_int_keys(...))
    """
    for k, v in d.items():
        k = int(k)
        if type(v) == dict:
            v = dict(convert_dict_to_use_int_keys(v))
        yield k, v


class DamageStateMappingMatrix:
    """
    This is a mapper for the damage state mapping matrix.
    It is necessary, because it is used in a transposed
    format compared to a normal dict.

    But in this format in can be read into
    pandas without further conversion.
    """

    def __init__(self, dict_conv_matrix):
        self.pure_dict_conv_matrix = dict_conv_matrix
        # do the init of the conv matrix lazy
        self.conv_matrix = None

    def _init_conv_matrix(self):
        self.conv_matrix = (
            pd.DataFrame(dict(convert_dict_to_use_int_keys(self.pure_dict_conv_matrix)))
            .transpose()
            .to_dict()
        )

    def contains_source_damage_state(self, source_damage_state_int):
        """
        Check if the source damage state is included in the
        matrix.
        """
        if self.conv_matrix is None:
            self._init_conv_matrix()
        return source_damage_state_int in self.conv_matrix.keys()

    def yield_target_damage_state_with_fraction(self, source_damage_state_int):
        """
        Returns a generator with the target damage state and the fraction
        of for the the specific target damage state.
        """
        for target_damage_state_int, fraction in self.conv_matrix[
            source_damage_state_int
        ].items():
            if fraction > 0:
                yield target_damage_state_int, fraction


class SchemaMapperResult:
    """
    Class to store the mapping results in.
    """

    def __init__(self, schema, taxonomy, damage_state, n_buildings):
        self.schema = schema
        self.taxonomy = taxonomy
        self.damage_state = damage_state
        self.n_buildings = n_buildings


SourceTargetSchemaTuple = collections.namedtuple(
    "SourceTargetSchemaTuple", "source_schema target_schema"
)

SourceTargetSchemaTaxonomyTuple = collections.namedtuple(
    "SourceTargetSchemaTaxonomyTuple",
    "source_schema target_schema source_taxonomy target_taxonomy",
)


class SchemaMapper:
    """
    Mapper class to map from one schema to anohter.
    """

    def __init__(self, tax_mapping_data, ds_mapping_data):
        self._tax_mapping_data = tax_mapping_data
        self._ds_mapping_data = ds_mapping_data

        self._cached_mappings = {}
        self._cached_mappings_taxonomy = {}

    @classmethod
    def from_taxonomy_and_damage_state_conversion_files(
        cls, tax_mapping_files, ds_mapping_files
    ):
        """
        Reads the data from files.
        """

        tax_mapping_data = []
        ds_mapping_data = []

        for mapping_file in tax_mapping_files:
            with open(mapping_file, "rt") as input_file:
                data = json.load(input_file)
                tax_mapping_data.append(data)

        for mapping_file in ds_mapping_files:
            with open(mapping_file, "rt") as input_file:
                data = json.load(input_file)
                ds_mapping_data.append(data)

        return cls.from_taxonomy_and_damage_state_conversion_data(
            tax_mapping_data, ds_mapping_data
        )

    @classmethod
    def from_taxonomy_and_damage_state_conversion_data(
        cls, tax_mapping_data, ds_mapping_data
    ):
        """
        Class method to init the data from a list of
        taxonomy related datasets
        and a list for the damage state related
        datasets.
        """

        # first make an index for the taxonomy schema
        # mapping datasets
        tax_mapping_data_by_schemas = {}
        for dataset in tax_mapping_data:
            source_schema = dataset["source_schema"]
            target_schema = dataset["target_schema"]
            conv_matrix = dataset["conv_matrix"]

            source_target_schema_tuple = SourceTargetSchemaTuple(
                source_schema=source_schema,
                target_schema=target_schema,
            )

            tax_mapping_data_by_schemas[source_target_schema_tuple] = conv_matrix

        # then to the very same for the damage state
        # schema mapping datasets
        # but here we need the target and the source taxonomies too
        ds_mapping_data_by_taxonomies = {}
        for dataset in ds_mapping_data:
            source_schema = dataset["source_schema"]
            target_schema = dataset["target_schema"]
            source_taxonomy = dataset["source_taxonomy"]
            target_taxonomy = dataset["target_taxonomy"]

            conv_matrix = DamageStateMappingMatrix(dataset["conv_matrix"])

            setting_tuple = SourceTargetSchemaTaxonomyTuple(
                source_schema=source_schema,
                target_schema=target_schema,
                source_taxonomy=source_taxonomy,
                target_taxonomy=target_taxonomy,
            )

            ds_mapping_data_by_taxonomies[setting_tuple] = conv_matrix
        return cls(tax_mapping_data_by_schemas, ds_mapping_data_by_taxonomies)

    def map_schema(
        self,
        source_schema,
        source_taxonomy,
        source_damage_state,
        target_schema,
        n_buildings=1.0,
    ):
        """
        Maps the data to another schema.
        """

        if source_schema == target_schema:
            return [
                SchemaMapperResult(
                    schema=source_schema,
                    taxonomy=source_taxonomy,
                    damage_state=source_damage_state,
                    n_buildings=n_buildings,
                )
            ]
        # otherwise we have to map
        results_for_1_building = self._map_schema_1(
            source_schema, source_taxonomy, source_damage_state, target_schema
        )

        results_for_n_buildings = []
        for result in results_for_1_building:
            results_for_n_buildings.append(
                SchemaMapperResult(
                    result.schema,
                    result.taxonomy,
                    result.damage_state,
                    result.n_buildings * n_buildings,
                )
            )

        return results_for_n_buildings

    def _map_schema_1(
        self, source_schema, source_taxonomy, source_damage_state, target_schema
    ):

        cachekey = CacheKey(
            source_schema, source_taxonomy, source_damage_state, target_schema
        )

        if cachekey in self._cached_mappings:
            return self._cached_mappings[cachekey]

        results = self._do_map_schema_1(
            source_schema, source_taxonomy, source_damage_state, target_schema
        )

        self._cached_mappings[cachekey] = results
        return results

    def _map_schema_1_just_taxonomy(
        self, source_schema, source_taxonomy, target_schema
    ):

        key = CacheKeyTaxonomy(
            source_schema=source_schema,
            source_taxonomy=source_taxonomy,
            target_schema=target_schema,
        )

        if key not in self._cached_mappings_taxonomy.keys():
            result = self._do_map_schema_1_just_taxonomy(
                source_schema=source_schema,
                source_taxonomy=source_taxonomy,
                target_schema=target_schema,
            )
            self._cached_mappings_taxonomy[key] = result
            return result

        return self._cached_mappings_taxonomy[key]

    def _do_map_schema_1_just_taxonomy(
        self, source_schema, source_taxonomy, target_schema
    ):

        source_target_schema_tuple = SourceTargetSchemaTuple(
            source_schema=source_schema,
            target_schema=target_schema,
        )
        if source_target_schema_tuple not in self._tax_mapping_data.keys():
            raise Exception(
                (
                    "There is no data for the schema "
                    + "mapping between the source schema "
                    + "{0} and the target schema {1}"
                ).format(source_schema, target_schema)
            )

        tax_conv_matrix = self._tax_mapping_data[source_target_schema_tuple]

        if source_taxonomy not in tax_conv_matrix.keys():
            raise Exception(
                (
                    "There is no data for the schema mapping "
                    + "for the source taxonomy {0}"
                ).format(source_taxonomy)
            )

        return tax_conv_matrix[source_taxonomy]

    def _do_map_schema_1(
        self, source_schema, source_taxonomy, source_damage_state, target_schema
    ):

        mapping_results = []

        tax_conv_row = self._map_schema_1_just_taxonomy(
            source_schema=source_schema,
            source_taxonomy=source_taxonomy,
            target_schema=target_schema,
        )

        for target_taxonomy in tax_conv_row.keys():
            n_buildings_in_target_taxonomy = 1.0 * tax_conv_row[target_taxonomy]

            if tax_conv_row[target_taxonomy] > 0:
                # now we can do the damage state conversion

                schema_taxonomy_setting = SourceTargetSchemaTaxonomyTuple(
                    source_schema=source_schema,
                    target_schema=target_schema,
                    source_taxonomy=source_taxonomy,
                    target_taxonomy=target_taxonomy,
                )

                if schema_taxonomy_setting not in self._ds_mapping_data.keys():
                    raise Exception(
                        (
                            "There is no data for the damage "
                            + "state schema mapping for "
                            + "target taxonomy {0} from source taxonomy {1}"
                        ).format(target_taxonomy, source_taxonomy)
                    )

                ds_conv_matrix = self._ds_mapping_data[schema_taxonomy_setting]

                if not ds_conv_matrix.contains_source_damage_state(source_damage_state):
                    raise Exception(
                        (
                            "There is no data for the damage state schema"
                            + " mapping for damage state {0}"
                        ).format(source_damage_state)
                    )

                for (
                    target_damage_state,
                    ds_fraction,
                ) in ds_conv_matrix.yield_target_damage_state_with_fraction(
                    source_damage_state
                ):
                    n_buildings_in_target_damage_state = (
                        n_buildings_in_target_taxonomy * ds_fraction
                    )

                    single_mapping_result = SchemaMapperResult(
                        schema=target_schema,
                        taxonomy=target_taxonomy,
                        damage_state=target_damage_state,
                        n_buildings=n_buildings_in_target_damage_state,
                    )

                    mapping_results.append(single_mapping_result)

        return mapping_results
