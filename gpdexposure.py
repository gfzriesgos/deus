#!/usr/bin/env python3

'''
Module for the exposure using a geopandas dataframe.
'''

import collections
import multiprocessing
import os

import numpy
import geopandas
import pandas


def read_exposure(filename):
    """
    Function to read the exposure from the file.
    """
    return geopandas.read_file(filename)


def str_Dx_to_int(damage_state_with_d_prefix):
    """
    Function to convert damage states.

    For example the input is D2 than the expected
    output is the number 2.
    """
    return int(damage_state_with_d_prefix[1:])


def int_x_to_str_Dx(damage_state_without_d_prefix):
    """
    Function to convert damage states.

    For exmple the input is 2 and the expected
    result is D2.
    """
    return 'D' + str(damage_state_without_d_prefix)


def update_exposure_transitions_and_losses(
        exposure,
        source_schema,
        schema_mapper,
        intensity_provider,
        fragility_provider,
        loss_provider):
    """
    This is the main function to update the
    exposure based on the intensities of the intensity provider.

    If the soruce_schema and the schema of the fragility provider
    doesn't match, then the schema_mapper will be used to map the
    exposure schema to the schema of the fragility functions.

    The result is a geopandas dataframe similar to the input dataframe,
    but with updated expo data, as well as fields for transitions
    (also dataframe), losses (aggregated value for all transitions as well
    as units) and the output schema.
    """

    updater = Updater(
        source_schema,
        fragility_provider,
        schema_mapper,
        intensity_provider,
        loss_provider
    )
    # So we use the pandas apply to run our function. I'm not sure if we
    # can parallize this, but it is one of the fastest ways in python anyway.

    n_cpus = multiprocessing.cpu_count()
    with multiprocessing.Pool(n_cpus) as pool:
        splitted_exposure = numpy.array_split(exposure, n_cpus)
        df = pandas.concat(
            pool.map(updater.update_df, splitted_exposure),
            sort=False
        )
        # This here is non parallized version, so that it is better to debug.
        # However, normally we want to be parallel.
        # df = pandas.concat(
        #     [updater.update_df(x) for x in splitted_exposure],
        #     sort=False
        # )
    return df


def zero():
    return 0


def map_exposure(
        expo,
        source_schema,
        target_schema,
        schema_mapper):
    """
    The function to map the exposure to another schema if necessary.
    """
    if source_schema == target_schema:
        return expo
    n_buildings = collections.defaultdict(zero)

    for _, row in expo.iterrows():
        # One taxonomy with a damage state can map to different other
        # taxonomies and different damage states.
        mapping_results = schema_mapper.map_schema(
            source_taxonomy=row.Taxonomy,
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

    # Create resulting dataframe.
    n_buildings_keys = len(n_buildings.keys())

    taxonomy = numpy.empty(n_buildings_keys, dtype=numpy.object)
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


def get_updated_exposure_and_transitions(
        geometry,
        expo,
        intensity_provider,
        fragility_provider):
    """
    This function returns the update exposure and all of
    the transitions that happend in this step.
    """
    if expo.Buildings.sum() == 0:
        # If we don't have any buildings we can't update
        # them and so we even don't need to read the intensity
        # for this cell.
        #
        # We just have to create the empty transitions dataframe.
        result_transitions = pandas.DataFrame({
            'taxonomy': numpy.empty(0, dtype=numpy.object),
            'from_damage_state': numpy.zeros(0),
            'to_damage_state': numpy.zeros(0),
            'n_buildings': numpy.zeros(0)
        })
        return expo, result_transitions
    # So now we need to check for updates in our exposure model.
    # First lets get the intensity for this cell.
    centroid = geometry.centroid
    lon, lat = centroid.x, centroid.y
    intensity, units = intensity_provider.get_nearest(lon=lon, lat=lat)

    transitions = collections.defaultdict(zero)
    n_buildings = collections.defaultdict(zero)

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
                intensity, units
            )

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
                transitions[key_transitions] += n_buildings_in_damage_state
        # If we have buildings left in the given damage state, than we must
        # add them in the n_buildings as well, but we don't need a transition.
        if n_left > 0:
            key_n_buildings = TaxonomyDamageStateTuple(
                taxonomy, old_damage_state
            )
            n_buildings[key_n_buildings] += n_left

    # And now we create the resulting dataframes out of our dicts.
    # First expo.
    expo_n_building_keys = len(n_buildings.keys())
    expo_taxonomy = numpy.empty(expo_n_building_keys, dtype=numpy.object)
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

    # Then the transitions.
    tran_n_keys = len(transitions.keys())
    tran_taxonomy = numpy.empty(tran_n_keys, dtype=numpy.object)
    tran_from_state = numpy.empty(tran_n_keys, dtype=numpy.int)
    tran_to_state = numpy.empty(tran_n_keys, dtype=numpy.int)
    tran_buildings = numpy.zeros(tran_n_keys)

    for idx, key in enumerate(transitions.keys()):
        tran_taxonomy[idx] = key.taxonomy
        tran_from_state[idx] = key.from_damage_state
        tran_to_state[idx] = key.to_damage_state
        tran_buildings = transitions[key]

    result_transitions = pandas.DataFrame({
        'taxonomy': tran_taxonomy,
        'from_damage_state': tran_from_state,
        'to_damage_state': tran_to_state,
        'n_buildings': tran_buildings
    })

    return result_expo, result_transitions


# This is our key for handling all of our transitions.
TransitionTuple = collections.namedtuple(
    'TransitionTuple',
    'taxonomy from_damage_state to_damage_state'
)
# This is our key for handling all of our n_buildings in
# the update step (we don't need the schema here).
TaxonomyDamageStateTuple = collections.namedtuple(
    'TaxonomyDamageStateTuple',
    'taxonomy damage_state'
)

# This is our key for the mapping (so we need the
# schema).
SchemaTaxonomyDamageStateTuple = collections.namedtuple(
    'SchemaTaxonomyDamageStateTuple',
    'schema taxonomy damage_state'
)


def compute_loss(transitions, loss_provider, schema):
    """
    Here we sum the loss over all the transitions.
    """
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


class Updater:
    """
    Class for running updates on the exposure.

    We use a class here to provide access to all the other
    data sources / providers, as a nested function can't be serialized
    for parallelization.
    """
    def __init__(
            self,
            source_schema,
            fragility_provider,
            schema_mapper,
            intensity_provider,
            loss_provider):
        self.source_schema = source_schema
        self.fragility_provider = fragility_provider
        self.schema_mapper = schema_mapper
        self.intensity_provider = intensity_provider
        self.loss_provider = loss_provider

    def update_df(self, df):
        """
        Runs the update for the update on each series of the
        given dataframe.
        """
        list_of_series = df.apply(self.update_series, axis=1)
        return geopandas.GeoDataFrame(list_of_series)

    def update_series(self, series):
        """
        This is the function that should be applied to *every* cell in the
        exposure.
        """
        # First we prepare our input.
        old_exposure = pandas.DataFrame(series.expo)
        old_exposure['Damage'] = old_exposure['Damage'].apply(str_Dx_to_int)

        # Then we need to map to the target schema.
        mapped_exposure = map_exposure(
            expo=old_exposure,
            source_schema=self.source_schema,
            target_schema=self.fragility_provider.schema,
            schema_mapper=self.schema_mapper
        )
        # Then we can collect the updates & transitions.
        updated_exposure, transitions = get_updated_exposure_and_transitions(
            geometry=series.geometry,
            expo=mapped_exposure,
            intensity_provider=self.intensity_provider,
            fragility_provider=self.fragility_provider
        )
        # After that we can compute the loss of all the transitions in the cell
        loss_value = compute_loss(
            transitions=transitions,
            loss_provider=self.loss_provider,
            schema=self.fragility_provider.schema)

        # At last step we need to convert the Damage column back to use the Dx
        # conversion (which we don't use in the map_exposure and
        # get_updated_exposure_and_transitions functions because of
        # performance).
        updated_exposure['Damage'] = updated_exposure[
            'Damage'
        ].apply(int_x_to_str_Dx)

        # In earlier versions of deus the updated exposure, the transitions
        # and the losses were splitted. In this version we merge them right
        # here. Later on we can split them back up to produce the expected
        # files.
        return pandas.Series({
            'gid': series.gid,
            'geometry': series.geometry,
            # We use the list orientation here to make the result more compact.
            # Normally it would use a dict orientiation that would make sense
            # for sparse output. It is not sparse here.
            # So we get out something like
            # {
            #  'Buildings': [0, 100, 23, ...],
            #  'Taxonomy': ['RC1', 'RC2', ...],
            #  ...
            # }
            'expo': updated_exposure.to_dict(orient='list'),
            'schema': self.fragility_provider.schema,
            'transitions': transitions.to_dict(orient='list'),
            'loss_value': loss_value,
            'loss_unit': self.loss_provider.get_unit()
        })
