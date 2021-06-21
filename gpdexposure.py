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

'''
Module for the exposure using a geopandas dataframe.
'''

import collections
import ctypes
import multiprocessing

import numpy
import geopandas
import pandas


PARALLEL_PROCESSING = True


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


ExpoKey = collections.namedtuple('ExpoKey', ['taxonomy', 'damage_state'])


class ExpoValues(ctypes.Structure):
    """Class to store the information for the values of an expo dict."""
    _fields_ = [
        ('buildings', ctypes.c_double),
        ('population', ctypes.c_double),
        ('replcostbdg', ctypes.c_double),
    ]

    def __repr__(self):
        return 'ExpoValues(' + \
            'buildings={0}, population={1}, replcostbdg={2})'.format(
                repr(self.buildings),
                repr(self.population),
                repr(self.replcostbdg)
            )


def empty_expo_values():
    """Return an empty expo value."""
    return ExpoValues(0, 0, 0)


TransitionKey = collections.namedtuple(
    'TransitionKey',
    ['taxonomy', 'from_damage_state', 'to_damage_state']
)


class TransitionValues(ctypes.Structure):
    """Class to store the keys in the transition dict."""
    _fields_ = [
        ('buildings', ctypes.c_double),
        ('replcostbdg', ctypes.c_double),
    ]

    def __repr__(self):
        return 'TransitionValues(buildings={0}, replcostbdg={1})'.format(
            repr(self.buildings), repr(self.replcostbdg)
        )


def empty_transition_values():
    """Return an empty transition value."""
    return TransitionValues(0, 0)


def zero():
    """Return 0."""
    return 0


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
    splitted_exposure = numpy.array_split(exposure, n_cpus)
    if PARALLEL_PROCESSING:
        with multiprocessing.Pool(n_cpus) as pool:
            dataframe = pandas.concat(
                pool.map(updater.update_df, splitted_exposure),
                sort=False
            )
    else:
        dataframe = pandas.concat(
            [updater.update_df(x) for x in splitted_exposure],
            sort=False
        )
    return dataframe


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
    result_expo = collections.defaultdict(empty_expo_values)

    # We have to collect the replacement costs over all
    # damage states of the results (for each taxonomy).
    n_buildings_per_tax = collections.defaultdict(zero)
    total_repl_per_tax = collections.defaultdict(zero)

    for old_expo_key, old_expo_value in expo.items():
        # One taxonomy with a damage state can map to different other
        # taxonomies and different damage states.
        mapping_results = schema_mapper.map_schema(
            source_taxonomy=old_expo_key.taxonomy,
            source_damage_state=old_expo_key.damage_state,
            source_schema=source_schema,
            target_schema=target_schema,
            # We want to keep it as a number between 0 and 1
            # so that we are able to map the population as well.
            n_buildings=1.0
        )

        for res in mapping_results:
            expo_key = ExpoKey(res.taxonomy, res.damage_state)
            # res.n_buildings is now only a number from 0 to 1.
            # So we need to do the multiplication ourselves
            # (but we can reuse the mapping value for others...)
            expo_value = result_expo[expo_key]

            new_buildings = res.n_buildings * old_expo_value.buildings
            expo_value.buildings += new_buildings
            n_buildings_per_tax[res.taxonomy] += new_buildings

            new_pop = res.n_buildings * old_expo_value.population
            expo_value.population += new_pop

            new_repl = new_buildings * old_expo_value.replcostbdg
            total_repl_per_tax[res.taxonomy] += new_repl

    for expo_key, expo_value in result_expo.items():
        taxonomy = expo_key.taxonomy
        n_bdg = n_buildings_per_tax[taxonomy]
        if n_bdg != 0:
            expo_value.replcostbdg = total_repl_per_tax[taxonomy] / n_bdg

    return result_expo


def get_updated_exposure_and_transitions(
        geometry,
        expo,
        intensity_provider,
        fragility_provider):
    """
    This function returns the update exposure and all of
    the transitions that happend in this step.
    """
    # Again, we can't be sure that those columns are there.
    # We use just zeros if they are not.
    result_transitions = collections.defaultdict(empty_transition_values)
    if not any(expo_value.buildings > 0 for expo_value in expo.values()):
        # If we don't have any buildings we can't update
        # them and so we even don't need to read the intensity
        # for this cell.
        return expo, result_transitions
    # So now we need to check for updates in our exposure model.
    # First lets get the intensity for this cell.
    centroid = geometry.centroid
    lon, lat = centroid.x, centroid.y
    intensity, units = intensity_provider.get_nearest(lon=lon, lat=lat)

    result_expo = collections.defaultdict(empty_expo_values)

    # Calculate the replacement costs for each taxonomy
    # before we care about the damage transitions.
    total_repl_per_tax = collections.defaultdict(zero)
    n_buildings_per_tax = collections.defaultdict(zero)

    for old_expo_key, old_expo_value in expo.items():
        n_left = old_expo_value.buildings
        n_pop_left = old_expo_value.population

        old_damage_state = old_expo_key.damage_state
        taxonomy = old_expo_key.taxonomy

        # We use the input data for calculating the weighted mean
        # for the replacment costs per building (in case they really
        # differ somehow, but the schemamapping makes this possible).
        total_repl_per_tax[taxonomy] += \
            (old_expo_value.replcostbdg * old_expo_value.buildings)
        n_buildings_per_tax[taxonomy] += old_expo_value.buildings

        damage_states_to_care = get_sorted_damage_states(
            fragility_provider,
            taxonomy,
            old_damage_state
        )

        for single_damage_state in damage_states_to_care:
            probability = single_damage_state.get_probability_for_intensity(
                intensity, units
            )
            expo_key = ExpoKey(taxonomy, single_damage_state.to_state)

            # We care about both the number of buildings and the population.
            n_buildings_in_damage_state = probability * n_left
            n_population_in_damage_state = probability * n_pop_left
            n_left -= n_buildings_in_damage_state
            n_pop_left -= n_population_in_damage_state

            if n_buildings_in_damage_state > 0:
                expo_value = result_expo[expo_key]

                expo_value.buildings += n_buildings_in_damage_state
                expo_value.population += n_population_in_damage_state

                transition_key = TransitionKey(
                    taxonomy, old_damage_state, single_damage_state.to_state
                )
                result_transitions[transition_key].buildings += \
                    n_buildings_in_damage_state

        # If we have buildings left in the given damage state, than we must
        # add them in the n_buildings as well, but we don't need a transition.
        if n_left > 0:
            expo_key = ExpoKey(taxonomy, old_damage_state)
            expo_value = result_expo[expo_key]
            expo_value.buildings += n_left
            expo_value.population += n_pop_left

    # Replacement costs per building; specific for the taxonomies
    repl_per_tax = collections.defaultdict(zero)

    # and update the replacement costs
    for taxonomy in total_repl_per_tax.keys():
        n_bdg = n_buildings_per_tax[taxonomy]
        if n_bdg != 0:
            repl_per_tax[taxonomy] = total_repl_per_tax[taxonomy] / n_bdg

    for expo_key, expo_value in result_expo.items():
        taxonomy = expo_key.taxonomy
        expo_value.replcostbdg = repl_per_tax[taxonomy]

    # We also put it into the transitions as those are used to
    # compute the loss later.
    for transition_key, transition_value in result_transitions.items():
        taxonomy = transition_key.taxonomy
        transition_value.replcostbdg = repl_per_tax[taxonomy]

    return result_expo, result_transitions


def compute_loss(transitions, loss_provider, schema):
    """Sum up all the loss over all the transitions."""
    loss_value = 0
    for transition_key, transition_value in transitions.items():
        replacement_cost = transition_value.replcostbdg
        # We want to use the replacement costs if those are given.
        # If we don't have replacement costs we can ask the loss_provider.
        if replacement_cost == 0:
            replacement_cost = loss_provider.get_fallback_replacement_cost(
                schema=schema,
                taxonomy=transition_key.taxonomy
            )

        single_loss_value = loss_provider.get_loss(
            schema=schema,
            taxonomy=transition_key.taxonomy,
            from_damage_state=transition_key.from_damage_state,
            to_damage_state=transition_key.to_damage_state,
            replacement_cost=replacement_cost
        )
        n_loss_value = single_loss_value * transition_value.buildings

        loss_value += n_loss_value
    return loss_value


def get_sorted_damage_states(
        fragility_provider,
        taxonomy,
        old_damage_state):
    """Return the sorted damage states that are above the the current one."""

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
    """Sort the damage states with the highest first."""
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

    def update_df(self, dataframe):
        """
        Runs the update for the update on each series of the
        given dataframe.
        """
        # In case that our subset is empty, we want to return None.
        # Otherwise our apply would return an empty geodataframe
        # with the columns of the input. But as this may contain
        # a name, we don't want that.
        if dataframe.empty:
            return None
        list_of_series = dataframe.apply(self.update_series, axis=1)
        return geopandas.GeoDataFrame(list_of_series)

    def update_series(self, series):
        """
        This is the function that should be applied to *every* cell in the
        exposure.
        """
        # First we prepare our input.
        old_exposure = expo_from_series_to_dict(series.expo)

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
            schema=self.fragility_provider.schema
        )
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
            'expo': updated_exposure_output_to_dict(updated_exposure),
            'schema': self.fragility_provider.schema,
            'transitions': transitions_output_to_dict(transitions),
            'loss_value': loss_value,
            'loss_unit': self.loss_provider.get_unit()
        })


def updated_exposure_output_to_dict(updated_exposure):
    """Convert to data to a dict for output."""
    result = {}
    for key in [
        'Taxonomy',
        'Damage',
        'Buildings',
        'Population',
        'Repl-cost-USD-bdg'
    ]:
        result[key] = [None] * len(updated_exposure)

    for idx, (expo_key, expo_value) in enumerate(
            updated_exposure.items()
    ):
        result['Taxonomy'][idx] = expo_key.taxonomy
        result['Damage'][idx] = int_x_to_str_Dx(expo_key.damage_state)
        result['Buildings'][idx] = expo_value.buildings
        result['Population'][idx] = expo_value.population
        result['Repl-cost-USD-bdg'][idx] = expo_value.replcostbdg

    return result


def transitions_output_to_dict(transitions):
    """Convert the transitions to a dict for output."""
    result = {}

    for key in [
        'taxonomy',
        'from_damage_state',
        'to_damage_state',
        'n_buildings',
        'replacement_costs_usd_bdg'
    ]:
        result[key] = [None] * len(transitions)

    for idx, (transition_key, transition_value) in enumerate(
            transitions.items()
    ):
        result['taxonomy'][idx] = transition_key.taxonomy
        result['from_damage_state'][idx] = transition_key.from_damage_state
        result['to_damage_state'][idx] = transition_key.to_damage_state
        result['n_buildings'][idx] = transition_value.buildings
        result['replacement_costs_usd_bdg'][idx] = transition_value.replcostbdg

    return result


def expo_from_series_to_dict(expo):
    """
    Convert the existing expo to an exposure dict (expo_keys & expo_values).

    The resulting expo is the one to work with in the mapping & the
    update function.
    """
    as_dict = collections.defaultdict(empty_expo_values)

    if isinstance(expo['Taxonomy'], list):
        idx_generator = range(len(expo['Taxonomy']))
    else:
        idx_generator = expo['Taxonomy'].keys()

    for idx in idx_generator:
        expo_key = ExpoKey(
            get_from_series_expo(expo['Taxonomy'], idx, None),
            str_Dx_to_int(get_from_series_expo(expo['Damage'], idx, None))
        )
        buildings = get_from_series_expo(expo.get('Buildings', []), idx, 0)
        population = get_from_series_expo(expo.get('Population', []), idx, 0)
        replcostbdg = get_from_series_expo(
            expo.get('Repl-cost-USD-bdg', []),
            idx,
            0
        )
        expo_value = ExpoValues(buildings, population, replcostbdg)
        as_dict[expo_key] = expo_value

    return as_dict


def get_from_series_expo(column, idx, default):
    """
    Get the values from the expo.

    This is a helper function only.
    """
    if isinstance(column, list):
        if idx < len(column):
            return column[idx]
        return default
    return column.get(idx, default)
