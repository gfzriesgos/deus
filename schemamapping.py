#!/usr/bin/env python3

'''
This is a module
for the mapping of the taxonomies.
'''

import collections
import json
import re

import pandas as pd


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

    @classmethod
    def from_taxonomy_and_damage_state_conversion_files(
            cls, tax_mapping_files, ds_mapping_files):

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

            tax_mapping_data_by_schemas[source_target_schema_tuple] = conv_matrix

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
        mapping_results = []

        source_target_schema_tuple = SourceTargetSchemaTuple(
            source_schema=source_schema,
            target_schema=target_schema,
        )
        if not source_target_schema_tuple in self._tax_mapping_data.keys():
            raise Exception('There is no data for the schema mapping between the source schema {0} and the target schema {1}'.format(source_schema, target_schema))

        tax_conv_matrix = self._tax_mapping_data[source_target_schema_tuple]

        if source_taxonomy not in tax_conv_matrix.keys():
            raise Exception('There is no data for the schema mapping for the source taxonomy {0}'.format(source_taxonomy))

        tax_conv_row = tax_conv_matrix[source_taxonomy]
        
        for target_taxonomy in tax_conv_row.keys():
            n_buildings_in_target_taxonomy = n_buildings * tax_conv_row[target_taxonomy]

            if tax_conv_row[target_taxonomy] > 0:
                # now we can do the damage state conversion

                schema_taxonomy_setting = SourceTargetSchemaTaxonomyTuple(
                    source_schema=source_schema,
                    target_schema=target_schema,
                    source_taxonomy=source_taxonomy,
                    target_taxonomy=target_taxonomy,
                )

                if schema_taxonomy_setting not in self._ds_mapping_data.keys():
                    raise Exception('There is no data for the damage state schema mapping for target taxonomy {0} from source taxonomy {1}'.format(target_taxonomy, source_taxonomy))

                ds_conv_matrix = self._ds_mapping_data[schema_taxonomy_setting]
                str_source_damage_state = str(source_damage_state)

                if str_source_damage_state not in ds_conv_matrix.index:
                    raise Exception('There is no data for teh damage state schema mapping for damage state {0}'.format(source_damage_state))

                ds_conv_row = ds_conv_matrix.loc[str_source_damage_state]

                for str_target_damage_state in ds_conv_row.keys():
                    # the keys in there are strings
                    n_buildings_in_target_damage_state = n_buildings_in_target_taxonomy * ds_conv_row[str_target_damage_state]

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




class TargetAndConvMatrix():
    '''
    Intermediate class for holding the target schema
    and building class as well as the conversion matrix
    for mapping to other damate states.
    '''
    def __init__(self, target_schema_and_building_class, conv_matrix):
        self._target_schema_and_building_class = \
            target_schema_and_building_class
        self._conv_matrix = conv_matrix

    def get_target_schema_and_building_class(self):
        '''
        Returns the target schema and builidng class in a format
        schema_building_class as in
        'Suppasri_2013_RC1' for the schema Suppasri_2013 and the
        building class RC1.
        '''
        return self._target_schema_and_building_class

    def get_conv_matrix(self):
        '''
        Returns the conversion matrix for the damage states.
        '''
        return self._conv_matrix

    def get_building_class(self, schema):
        '''
        Returns the building class name.
        '''
        return re.sub(
            r'^' + schema + '_',
            '',
            self._target_schema_and_building_class
        )

    def is_for_schema(self, schema):
        '''
        True if the target data is for the given schema.
        '''
        return self._target_schema_and_building_class.startswith(schema)


class BuildingClassSpecificDamageStateMapper():
    '''
    This is a schema mapper that contains data for
    mapping the building classes and damage states.
    The specific part here is that also the damage state
    mapping is building class specific.
    '''

    def __init__(self, mapping_data):
        self._mapping_data = mapping_data

    def map_schema(self,
                   source_taxonomy,
                   source_damage_state,
                   source_schema,
                   target_schema,
                   n_buildings=1.0):
        '''
        Maps a building class with a damage state and n buildings
        to another schema (with possible several damage states and
        several different building classes).
        Here it uses the data for damage state mappings that is
        specific for each building class.
        '''
        if source_schema == target_schema:
            return [SchemaMapperResult(
                taxonomy=source_taxonomy,
                damage_state=source_damage_state,
                n_buildings=n_buildings)]

        result = []

        from_schema_and_building_class = \
            source_schema + '_' + source_taxonomy

        if from_schema_and_building_class not in self._mapping_data.keys():
            raise Exception('There is no data to map from {0}'.format(
                from_schema_and_building_class
            ))

        target_list = self._mapping_data[from_schema_and_building_class]

        target_list_with_target_schema = [
            x for x in target_list
            if x.is_for_schema(target_schema)
        ]

        if not target_list_with_target_schema:
            raise Exception('There is no data to map from {0}'.format(
                from_schema_and_building_class
            ))

        for target_data in target_list_with_target_schema:
            target_building_class = target_data.get_building_class(
                target_schema
            )
            conv_matrix = target_data.get_conv_matrix()[
                str(source_damage_state)
            ]

            for target_damage_state in conv_matrix.keys():
                result.append(
                    BuildingClassSpecificDamageStateMapper
                    ._map_damage_state_to_result(
                        conv_matrix,
                        target_building_class,
                        target_damage_state,
                        n_buildings
                    )
                )
        return result

    @staticmethod
    def _map_damage_state_to_result(
            conv_matrix,
            target_building_class,
            target_damage_state,
            n_buildings):
        '''
        Compute the number of buildings for the damage states
        and return the SchemaMapperResult.
        '''
        mapping_value = conv_matrix[
            target_damage_state
        ]
        n_buildings_in_damage_state = mapping_value * n_buildings

        return SchemaMapperResult(
            taxonomy=target_building_class,
            damage_state=target_damage_state,
            n_buildings=n_buildings_in_damage_state
        )

    @classmethod
    def from_files(cls, files):
        '''
        Reads the data from a list of files.
        '''
        data = []
        for single_file in files:
            with open(single_file, 'rt') as input_file:
                single_data = json.load(input_file)
                data.append(single_data)
        return cls.from_list_of_dicts(data)

    @classmethod
    def from_list_of_dicts(cls, list_of_dicts):
        '''
        Reads the data from a list of files.
        '''
        mapping_data = {}

        for single_dict in list_of_dicts:
            from_schema_and_building_class = (
                single_dict['source_schema']
                +
                '_'
                +
                single_dict['source_taxonomy']
            )
            to_schema_and_building_class = (
                single_dict['target_schema']
                +
                '_'
                +
                single_dict['target_taxonomy']
            )
            conv_matrix = single_dict['conv_matrix']

            if from_schema_and_building_class not in mapping_data.keys():
                mapping_data[from_schema_and_building_class] = []

            mapping_data[from_schema_and_building_class].append(
                TargetAndConvMatrix(to_schema_and_building_class, conv_matrix)
            )

        return cls(mapping_data)


class SchemaMapperOld():
    '''
    This schema mapper combines the mapping of building classes
    and of damage states into one class.
    '''
    def __init__(self, building_class_mapper, damage_state_mapper):
        self._building_class_mapper = building_class_mapper
        self._damage_state_mapper = damage_state_mapper

    def get_building_class_mapper(self):
        '''
        Returns the building class mapper.
        '''
        return self._building_class_mapper

    def get_damage_state_mapper(self):
        '''
        Returns the damage state mapper.
        '''
        return self._damage_state_mapper

    def map_schema(self,
                   source_taxonomy,
                   source_damage_state,
                   source_schema,
                   target_schema,
                   n_buildings=1.0):
        '''
        Maps a building class with a damage state and n buildings
        to another schema (with possible several damage states and
        several different building classes).
        '''
        if source_schema == target_schema:
            return [SchemaMapperResult(
                taxonomy=source_taxonomy,
                damage_state=source_damage_state,
                n_buildings=n_buildings)]

        result = []
        building_class_mapping_results = \
            self._building_class_mapper.map_building_class(
                taxonomy=source_taxonomy,
                source_schema=source_schema,
                target_schema=target_schema,
                n_buildings=n_buildings,
            )

        for bc_mapping in building_class_mapping_results:
            damage_state_mapping_results = \
                self._damage_state_mapper.map_damage_state(
                    source_damage_state=source_damage_state,
                    source_schema=source_schema,
                    target_schema=target_schema,
                    n_buildings=1.0
                )

            for ds_mapping in damage_state_mapping_results:
                result.append(
                    SchemaMapperResult(
                        taxonomy=bc_mapping.get_building_class(),
                        damage_state=ds_mapping.get_damage_state(),
                        n_buildings=bc_mapping.get_n_buildings() *
                        ds_mapping.get_n_buildings())
                )
        return result


class SchemaMapperResultOld():
    '''
    Result class for the schema mapping.
    '''
    def __init__(self, taxonomy, damage_state, n_buildings):
        self._taxonomy = taxonomy
        self._damage_state = damage_state
        self._n_buildings = n_buildings

    def get_taxonomy(self):
        '''
        Returns the building class.
        '''
        return self._taxonomy

    def get_damage_state(self):
        '''
        Returns the damage state.
        '''
        return self._damage_state

    def get_n_buildings(self):
        '''
        Returns the number of buildings with the damage
        state and the building class.
        '''
        return self._n_buildings


class DamageStateMapperResult():
    '''
    Class to represent the resulting damage states after
    the mapping.
    '''
    def __init__(self, damage_state, n_buildings):
        self._damage_state = damage_state
        self._n_buildings = n_buildings

    def get_damage_state(self):
        '''
        Returns the damage state.
        '''
        return self._damage_state

    def get_n_buildings(self):
        '''
        Returns the number of buildings in this
        damage state.
        '''
        return self._n_buildings

    def __repr__(self):
        return 'DamageStateMapperResult(' + \
                'damage_state={0}, n_buildings={1})'.format(
                    repr(self._damage_state),
                    repr(self._n_buildings))


class DamageStateMapper():
    '''
    This is the mapper for the damage state only.
    '''

    def __init__(self, data):
        self._data = data

    def map_damage_state(
            self,
            source_damage_state,
            source_schema,
            target_schema,
            n_buildings=1):
        '''
        Maps one damage state from one schema
        to other damage states.
        '''
        if source_schema == target_schema:
            return [DamageStateMapperResult(
                source_damage_state, n_buildings)]
        result = []
        possible_mappings = [
            entry for entry in self._data
            if entry['source_schema'] == source_schema
            and entry['target_schema'] == target_schema
        ]
        if not possible_mappings:
            raise Exception('There is no data to map from {0} to {1}'.format(
                source_schema, target_schema))
        conv_matrix = possible_mappings[0]['conv_matrix']

        settings_for_ds = conv_matrix[str(source_damage_state)]

        for target_damage_state in settings_for_ds.keys():
            proportion = settings_for_ds[target_damage_state]
            if proportion > 0:
                result.append(
                    DamageStateMapperResult(
                        int(target_damage_state),
                        proportion*n_buildings))

        return result

    @classmethod
    def from_files(cls, files):
        '''
        Reads the data from a list of files.
        '''
        data = []
        for single_file in files:
            with open(single_file, 'rt') as input_file:
                single_data = json.load(input_file)
                single_data['conv_matrix'] = json.loads(
                    single_data['conv_matrix'])
                data.append(single_data)
        return cls(data)


class BuildingClassMapperResult():
    '''
    Class to represent the result building class
    after the mapping.
    '''
    def __init__(self, building_class, n_buildings):
        self._building_class = building_class
        self._n_buildings = n_buildings

    def get_building_class(self):
        '''
        Returns the building class.
        '''
        return self._building_class

    def get_n_buildings(self):
        '''
        Returns the number of buildings in this
        building class.
        '''
        return self._n_buildings

    def __repr__(self):
        return 'BuildingClassMapperResult(' + \
            'building_class={0}, n_buildings={1})'.format(
                repr(self._building_class),
                repr(self._n_buildings))


class BuildingClassMapper():
    '''
    This is the mapper for the building classes only.
    '''

    def __init__(self, data):
        self._data = data

    def map_building_class(
            self,
            taxonomy,
            source_schema,
            target_schema,
            n_buildings=1):
        '''
        Maps one building class from one schema
        to other building classes.
        '''
        if source_schema == target_schema:
            return [BuildingClassMapperResult(
                taxonomy, n_buildings)]
        result = []
        possible_mappings = [
            entry for entry in self._data
            if entry['source_schema'] == source_schema
            and entry['target_schema'] == target_schema
        ]
        if not possible_mappings:
            raise Exception('There is no data to map from {0} to {1}'.format(
                source_schema, target_schema))
        conv_matrix = possible_mappings[0]['conv_matrix']

        settings_for_bc = conv_matrix[taxonomy]

        for target_building_class in settings_for_bc.keys():
            proportion = settings_for_bc[target_building_class]
            if proportion > 0:
                result.append(
                    BuildingClassMapperResult(
                        target_building_class,
                        proportion*n_buildings))
        return result

    @classmethod
    def from_files(cls, files):
        '''
        Reads the data from a list of files.
        '''
        data = []
        for single_file in files:
            with open(single_file, 'rt') as input_file:
                single_data = json.load(input_file)
                single_data['conv_matrix'] = json.loads(
                    single_data['conv_matrix'])
                data.append(single_data)
        return cls(data)
