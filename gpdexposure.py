#!/usr/bin/env python3

'''
Module for the exposure using a geopandas dataframe.
'''

import collections
import os

import numpy
import geopandas
import pandas


def read_exposure(filename):
    return geopandas.read_file(filename)

def update_exposure_transitions_and_losses(exposure, source_schema, schema_mapper,
        intensity_provider, fragility_provider, loss_provider):
    def f(series):
        old_exposure = pandas.DataFrame(series.expo)
        old_exposure['Damage'] = old_exposure['Damage'].apply(lambda x: int(x[1:]))
        mapped_exposure = map_exposure(
            expo=old_exposure,
            source_schema=source_schema,
            target_schema=fragility_provider.schema,
            schema_mapper=schema_mapper
        )
        updated_exposure, transitions = get_updated_exposure_and_transitions(
            series.geometry, mapped_exposure,
            intensity_provider, fragility_provider
        )
        loss_value = compute_loss(transitions, loss_provider, fragility_provider.schema)
        updated_exposure['Damage'] = updated_exposure['Damage'].apply(lambda x: 'D' + str(x))
        return pandas.Series({
            'gid': series.gid,
            'geometry': series.geometry,
            'expo': updated_exposure,
            'schema': fragility_provider.schema,
            'transitions': transitions,
            'loss_value': loss_value,
            'loss_unit': 'USD'

        })
    list_of_series = exposure.apply(f, axis=1)
    as_data_frame = pandas.DataFrame(list_of_series)
    gdf = geopandas.GeoDataFrame(as_data_frame, geometry=as_data_frame.geometry)
    return gdf

def map_exposure(expo, source_schema, target_schema, schema_mapper):
    if source_schema == target_schema:
        return expo
    n_buildings = collections.defaultdict(lambda: 0)
    
    for _, row in expo.iterrows():
        mapping_results = schema_mapper.map_schema(
            source_taxonomy=row.Taxonomy,
            # convert into number
            source_damage_state=row.Damage,
            source_schema=source_schema,
            target_schema=target_schema,
            n_buildings=row.Buildings
        )

        for res in mapping_results:

            key = SchemaTaxonomyDamageStateTuple(
                schema=target_schema,
                taxonomy=res.taxonomy,
                damage_state=res.damage_state
            )
            n_buildings[key] = n_buildings[key] + res.n_buildings

    n_buildings_keys = len(n_buildings.keys())

    taxonomy = numpy.chararray(n_buildings_keys)
    damage = numpy.empty(n_buildings_keys, dtype=numpy.int)
    buildings = numpy.zeros(n_buildings_keys)

    for idx, key in enumerate(n_buildings.keys()):
        taxonomy[idx] = key.taxonomy
        damage[idx] = key.damage_state
        buildings[idx] = n_buildings[key]

    return pandas.DataFrame({
        'Taxonomy': taxonomy,
        'Damage': damage,
        'Buildings': buildings,
    })

def get_updated_exposure_and_transitions(geometry, expo, intensity_provider, fragility_provider):
    centroid = geometry.centroid
    lon, lat = centroid.x, centroid.y
    intensity, units = intensity_provider.get_nearest(lon=lon, lat=lat)

    transitions = collections.defaultdict(lambda: 0)
    n_buildings = collections.defaultdict(lambda: 0)

    for _, row in expo.iterrows():
        n_left = row.Buildings
        old_damage_state = row.Damage
        taxonomy = row.Taxonomy
        damage_states_to_care = get_sorted_damage_states(
            fragility_provider,
            taxonomy,
            old_damage_state
        )

        for single_damage_state in damage_states_to_care:
            probability = single_damage_state.get_probability_for_intensity(
                intensity, units)

            n_buildings_in_damage_state = probability * n_left
            n_left -= n_buildings_in_damage_state


            if n_buildings_in_damage_state > 0:
                key_n_buildings = TaxonomyDamageStateTuple(
                    taxonomy, single_damage_state.to_state
                )
                n_buildings[key_n_buildings] += n_buildings_in_damage_state

                key_transitions = TransitionTuple(
                    taxonomy, old_damage_state, single_damage_state.to_state
                )
                transitions[key] += n_buildings_in_damage_state

        expo_n_building_keys = len(n_buildings.keys())
        expo_taxonomy = numpy.chararray(expo_n_building_keys)
        expo_damage = numpy.empty(expo_n_building_keys, dtype=numpy.int)
        expo_buildings = numpy.zeros(expo_n_building_keys)

        for idx, key in enumerate(n_buildings.keys()):
            expo_taxonomy[idx] = key.taxonomy
            expo_damage[idx] = key.damage_state
            expo_buildings[idx] = n_buildings[key]

        result_expo = pandas.DataFrame({
            'Taxonomy': expo_taxonomy,
            'Damage': expo_damage,
            'Buildings': expo_buildings
        })

        tran_n_keys = len(transitions.keys())

        tran_taxonomy = numpy.chararray(tran_n_keys)
        tran_from_state = numpy.empty(tran_n_keys, dtype=numpy.int)
        tran_to_state = numpy.empty(tran_n_keys, dtype=numpy.int)
        tran_buildings = numpy.zeros(tran_n_keys)

        result_transitions = pandas.DataFrame({
            'taxonomy': tran_taxonomy,
            'from_damage_state': tran_from_state,
            'to_damage_state': tran_to_state,
            'n_buildings': tran_buildings
        })

        return result_expo, result_transitions


TransitionTuple = collections.namedtuple(
    'TransitionTuple',
    'taxonomy from_damage_state to_damage_state'
)

TaxonomyDamageStateTuple = collections.namedtuple(
    'TaxonomyDamageStateTuple',
    'taxonomy damage_state'
)


SchemaTaxonomyDamageStateTuple = collections.namedtuple(
    'SchemaTaxonomyDamageStateTuple',
    'schema taxonomy damage_state'
)

def compute_loss(transitions, loss_provider, schema):
    loss_value = 0
    for _, row in transitions.iterrows():
        single_loss_value = loss_provider.get_loss(
            schema=schema,
            taxonomy=row.taxonomy,
            from_damage_state=row.from_damage_state,
            to_damage_state=row.to_damage_state
        )
        n_loss_value = single_loss_value * row.n_buildings

        loss_value += n_loss_value
    return loss_value


def get_sorted_damage_states(
        fragility_provider,
        taxonomy,
        old_damage_state):
    '''
    Returns the sorted damage states
    that are above the the current one.
    '''

    damage_states = fragility_provider.get_damage_states_for_taxonomy(
        taxonomy
    )

    damage_states_to_care = [
        ds for ds in damage_states
        if ds.from_state == old_damage_state
        and ds.to_state > old_damage_state
    ]

    damage_states_to_care.sort(key=sort_by_to_damage_state_desc)

    return damage_states_to_care


def sort_by_to_damage_state_desc(damage_state):
    '''
    Function to sort the damage states by to_damage_state
    desc.
    '''
    return damage_state.to_state * -1
