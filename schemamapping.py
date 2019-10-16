#!/usr/bin/env python3

'''
This is a module
for the mapping of the taxonomies.
'''

import json
import re


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


class SchemaMapper():
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


class SchemaMapperResult():
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
