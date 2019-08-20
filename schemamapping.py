#!/usr/bin/env python3

'''
This is a module
for the mapping of the taxonomies.
'''

import json


class SchemaMapper():
    '''
    This schema mapper combines the mapping of building classes
    and of damage states into one class.
    '''
    def __init__(self, building_class_mapper, damage_state_mapper):
        self._building_class_mapper = building_class_mapper
        self._damage_state_mapper = damage_state_mapper

    def map_schema(self,
                   source_building_class,
                   source_damage_state,
                   source_name,
                   target_name,
                   n_buildings=1.0):
        '''
        Maps a building class with a damage state and n buildings
        to another schema (with possible several damage states and
        several different building classes).
        '''
        if source_name == target_name:
            return [SchemaMapperResult(
                building_class=source_building_class,
                damage_state=source_damage_state,
                n_buildings=n_buildings)]

        result = []
        building_class_mapping_results = \
            self._building_class_mapper.map_building_class(
                source_building_class=source_building_class,
                source_name=source_name,
                target_name=target_name,
                n_buildings=n_buildings,
            )

        for bc_mapping in building_class_mapping_results:
            damage_state_mapping_results = \
                self._damage_state_mapper.map_damage_state(
                    source_damage_state=source_damage_state,
                    source_name=source_name,
                    target_name=target_name,
                    n_buildings=1.0
                )

            for ds_mapping in damage_state_mapping_results:
                result.append(
                    SchemaMapperResult(
                        building_class=bc_mapping.get_building_class(),
                        damage_state=ds_mapping.get_damage_state(),
                        n_buildings=bc_mapping.get_n_buildings() *
                        ds_mapping.get_n_buildings())
                )
        return result


class SchemaMapperResult():
    '''
    Result class for the schema mapping.
    '''
    def __init__(self, building_class, damage_state, n_buildings):
        self._building_class = building_class
        self._damage_state = damage_state
        self._n_buildings = n_buildings

    def get_building_class(self):
        '''
        Returns the building class.
        '''
        return self._building_class

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


class TaxonomyMapper():
    '''
    This class is the taxonomy mapper.
    '''
    def __init__(self, damage_state_mapper):
        self._damage_state_mapper = damage_state_mapper

    # TODO
    # it is also necessary to add the number of buildings
    # or to care about the splitting of the in different
    # building classes and different damage states
    def find_fragility_taxonomy_and_new_exposure_taxonomy(
            self,
            exposure_taxonomy,
            actual_damage_state,
            fragility_taxonomies):
        '''
        Finds the taxonomy for the fragility functions
        with for the given exposure taxonomy.

        Can return a different exposure taxonomy to use
        for updating the exposure file in case of
        a schema switch (as for switching from tsunamis to
        earth quake hazards).

        As on the mapping process it is also possible to
        map from one building class to another one with
        a different damage state, we also give back the
        new damage state.
        '''
        # TODO
        # here it will only take the very first fragility_taxonomy
        # and it will stay with the existing exposure_taxonomy
        # (but this may be changed in case of a different schema for
        # the fragility; this will be the case for switching to tsunami
        # fragility function).
        return (
            [*fragility_taxonomies][0],
            exposure_taxonomy,
            actual_damage_state,
        )


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
            source_name,
            target_name,
            n_buildings=1):
        '''
        Maps one damage state from one schema
        to other damage states.
        '''
        if source_name == target_name:
            return [DamageStateMapperResult(
                source_damage_state, n_buildings)]
        result = []
        possible_mappings = [
            entry for entry in self._data
            if entry['source_name'] == source_name
            and entry['target_name'] == target_name
        ]
        if not possible_mappings:
            raise Exception('There is no data to map from {0} to {1}'.format(
                source_name, target_name))
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
            source_building_class,
            source_name,
            target_name,
            n_buildings=1):
        '''
        Maps one building class from one schema
        to other building classes.
        '''
        if source_name == target_name:
            return [BuildingClassMapperResult(
                source_building_class, n_buildings)]
        result = []
        possible_mappings = [
            entry for entry in self._data
            if entry['source_name'] == source_name
            and entry['target_name'] == target_name
        ]
        if not possible_mappings:
            raise Exception('There is no data to map from {0} to {1}'.format(
                source_name, target_name))
        conv_matrix = possible_mappings[0]['conv_matrix']

        settings_for_bc = conv_matrix[source_building_class]

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
