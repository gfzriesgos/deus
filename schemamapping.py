#!/usr/bin/env python3

'''
This is a module
for the mapping of the taxonomies.
'''

import collections
import json

import pandas as pd


CacheKey = collections.namedtuple(
    'CacheKey',
    'source_schema source_taxonomy source_damage_state target_schema'
)


class SchemaMapperResult():
    """
    Class to store the mapping results in.
    """
    def __init__(
            self,
            schema,
            taxonomy,
            damage_state,
            n_buildings):
        self._schema = schema
        self._taxonomy = taxonomy
        self._damage_state = damage_state
        self._n_buildings = n_buildings

    def get_schema(self):
        """Returns the schema."""
        return self._schema

    def get_taxonomy(self):
        """Returns the taxonomy."""
        return self._taxonomy

    def get_damage_state(self):
        """Returns the damage state (as number)."""
        return self._damage_state

    def get_n_buildings(self):
        """Returns the number of buildings."""
        return self._n_buildings


SourceTargetSchemaTuple = collections.namedtuple(
    'SourceTargetSchemaTuple',
    'source_schema target_schema'
)

SourceTargetSchemaTaxonomyTuple = collections.namedtuple(
    'SourceTargetSchemaTaxonomyTuple',
    'source_schema target_schema source_taxonomy target_taxonomy'
)


class SchemaMapper():
    """
    Mapper class to map from one schema to anohter.
    """
    def __init__(self, tax_mapping_data, ds_mapping_data):
        self._tax_mapping_data = tax_mapping_data
        self._ds_mapping_data = ds_mapping_data

        self._cached_mappings = {}

    @classmethod
    def from_taxonomy_and_damage_state_conversion_files(
            cls, tax_mapping_files, ds_mapping_files):
        """
        Reads the data from files.
        """

        tax_mapping_data = []
        ds_mapping_data = []

        for mapping_file in tax_mapping_files:
            with open(mapping_file, 'rt') as input_file:
                data = json.load(input_file)
                tax_mapping_data.append(data)

        for mapping_file in ds_mapping_files:
            with open(mapping_file, 'rt') as input_file:
                data = json.load(input_file)
                ds_mapping_data.append(data)

        return cls.from_taxonomy_and_damage_state_conversion_data(
            tax_mapping_data, ds_mapping_data)

    @classmethod
    def from_taxonomy_and_damage_state_conversion_data(
            cls, tax_mapping_data, ds_mapping_data):
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
            source_schema = dataset['source_schema']
            target_schema = dataset['target_schema']
            conv_matrix = dataset['conv_matrix']

            source_target_schema_tuple = SourceTargetSchemaTuple(
                source_schema=source_schema,
                target_schema=target_schema,
            )

            tax_mapping_data_by_schemas[
                source_target_schema_tuple
            ] = conv_matrix

        # then to the very same for the damage state
        # schema mapping datasets
        # but here we need the target and the source taxonomies too
        ds_mapping_data_by_taxonomies = {}
        for dataset in ds_mapping_data:
            source_schema = dataset['source_schema']
            target_schema = dataset['target_schema']
            source_taxonomy = dataset['source_taxonomy']
            target_taxonomy = dataset['target_taxonomy']

            conv_matrix = pd.DataFrame(dataset['conv_matrix'])

            setting_tuple = SourceTargetSchemaTaxonomyTuple(
                source_schema=source_schema,
                target_schema=target_schema,
                source_taxonomy=source_taxonomy,
                target_taxonomy=target_taxonomy,
            )

            ds_mapping_data_by_taxonomies[setting_tuple] = conv_matrix
        return cls(
            tax_mapping_data_by_schemas,
            ds_mapping_data_by_taxonomies)

    def map_schema(
            self,
            source_schema,
            source_taxonomy,
            source_damage_state,
            target_schema,
            n_buildings=1.0):
        """
        Maps the data to another schema.
        """

        if source_schema == target_schema:
            return [
                SchemaMapperResult(
                    schema=source_schema,
                    taxonomy=source_taxonomy,
                    damage_state=source_damage_state,
                    n_buildings=n_buildings
                )
            ]
        # otherwise we have to map
        results_for_1_building = self._map_schema_1(
            source_schema,
            source_taxonomy,
            source_damage_state,
            target_schema
        )

        results_for_n_buildings = []
        for result in results_for_1_building:
            results_for_n_buildings.append(
                SchemaMapperResult(
                    result.get_schema(),
                    result.get_taxonomy(),
                    result.get_damage_state(),
                    result.get_n_buildings() * n_buildings
                )
            )

        return results_for_n_buildings

    def _map_schema_1(
            self,
            source_schema,
            source_taxonomy,
            source_damage_state,
            target_schema):

        cachekey = CacheKey(
            source_schema,
            source_taxonomy,
            source_damage_state,
            target_schema
        )

        if cachekey in self._cached_mappings:
            return self._cached_mappings[cachekey]

        results = self._do_map_schema_1(
            source_schema,
            source_taxonomy,
            source_damage_state,
            target_schema
        )

        self._cached_mappings[cachekey] = results
        return results

    def _do_map_schema_1(
            self,
            source_schema,
            source_taxonomy,
            source_damage_state,
            target_schema):

        mapping_results = []
        source_target_schema_tuple = SourceTargetSchemaTuple(
            source_schema=source_schema,
            target_schema=target_schema,
        )
        if source_target_schema_tuple not in self._tax_mapping_data.keys():
            raise Exception(
                (
                    'There is no data for the schema ' +
                    'mapping between the source schema ' +
                    '{0} and the target schema {1}'
                ).format(source_schema, target_schema))

        tax_conv_matrix = self._tax_mapping_data[source_target_schema_tuple]

        if source_taxonomy not in tax_conv_matrix.keys():
            raise Exception(
                (
                    'There is no data for the schema mapping ' +
                    'for the source taxonomy {0}'
                ).format(source_taxonomy))

        tax_conv_row = tax_conv_matrix[source_taxonomy]

        for target_taxonomy in tax_conv_row.keys():
            n_buildings_in_target_taxonomy = (
                1.0 * tax_conv_row[target_taxonomy]
            )

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
                            'There is no data for the damage ' +
                            'state schema mapping for ' +
                            'target taxonomy {0} from source taxonomy {1}'
                        ).format(target_taxonomy, source_taxonomy))

                ds_conv_matrix = self._ds_mapping_data[schema_taxonomy_setting]
                str_source_damage_state = str(source_damage_state)

                if str_source_damage_state not in ds_conv_matrix.index:
                    raise Exception(
                        (
                            'There is no data for the damage state schema' +
                            ' mapping for damage state {0}'
                        ).format(source_damage_state))

                ds_conv_row = ds_conv_matrix.loc[str_source_damage_state]

                for str_target_damage_state in ds_conv_row.keys():
                    # the keys in there are strings
                    n_buildings_in_target_damage_state = (
                        n_buildings_in_target_taxonomy *
                        ds_conv_row[str_target_damage_state]
                    )

                    if ds_conv_row[str_target_damage_state] > 0:
                        target_damage_state = int(str_target_damage_state)

                        single_mapping_result = SchemaMapperResult(
                            schema=target_schema,
                            taxonomy=target_taxonomy,
                            damage_state=target_damage_state,
                            n_buildings=n_buildings_in_target_damage_state
                        )

                        mapping_results.append(single_mapping_result)

        return mapping_results
