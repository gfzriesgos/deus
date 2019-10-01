#!/usr/bin/env python3

'''
Module for the exposure related classes.
'''

import math
import re

import pandas as pd
import geopandas as gpd

import transition


class ExposureCellList():
    '''
    List of exposure cells.
    '''
    def __init__(self, exposure_cells):
        self._exposure_cells = exposure_cells

    def get_exposure_cells(self):
        '''
        Returns the list of exposure cells.
        '''
        return self._exposure_cells

    def append(self, exposure_cell):
        '''
        Appends an exposure cell.
        There is no logic to merge cells.
        '''
        self._exposure_cells.append(exposure_cell)

    def map_schema(self, target_schema, schema_mapper):
        '''
        Maps one whole list to a different schema.
        '''
        elements = []
        for exposure_cell in self._exposure_cells:
            mapped_cell = exposure_cell.map_schema(
                target_schema,
                schema_mapper
            )
            elements.append(mapped_cell)
        return ExposureCellList(elements)

    @classmethod
    def from_dataframe(cls, schema, dataframe):
        '''
        Reads the list from a dataframe.
        '''
        elements = []
        for _, row in dataframe.iterrows():
            exposure_cell = ExposureCell.from_series(
                series=row,
                schema=schema
            )
            elements.append(exposure_cell)
        return cls(elements)

    @classmethod
    def from_simple_dataframe(cls, schema, dataframe):
        '''
        Reads the list from a more simple dataframe (with
        the taxonomies in the rows).
        '''
        elements = []
        for _, row in dataframe.iterrows():
            exposure_cell = ExposureCell.from_simple_series(
                series=row,
                schema=schema
            )
            elements.append(exposure_cell)
        return cls(elements)

    @classmethod
    def from_file(cls, schema, file_name):
        '''
        Reads the list from a file.
        '''
        gdf = gpd.GeoDataFrame.from_file(file_name)
        if 'expo' in gdf.columns:
            return cls.from_dataframe(schema, gdf)
        return cls.from_simple_dataframe(schema, gdf)

    def to_simple_dataframe(self):
        '''
        Converts the list to a simple dataframe (with
        taxonomies as rows).
        '''
        series = [x.to_simple_series() for x in self._exposure_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])

    def to_dataframe(self):
        '''
        Converts the list to a dataframe with subdataframes
        for each cell (information about the taxonomies and
        the damage states seperated).
        '''
        series = [x.to_series() for x in self._exposure_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])


class ExposureCell():
    '''
    Spatial cell with the exposure data.
    '''
    def __init__(self, schema, gid, name, geometry, taxonomies):
        self._schema = schema
        self._gid = gid
        self._name = name
        self._geometry = geometry
        self._taxonomies = taxonomies

    def get_schema(self):
        '''
        Returns the schema.
        '''
        return self._schema

    def get_gid(self):
        '''
        Returns the gid.
        '''
        return self._gid

    def get_name(self):
        '''
        Returns the name.
        '''
        return self._name

    def get_geometry(self):
        '''
        Returns the geometry of the cell.
        '''
        return self._geometry

    def get_lon_lat_of_centroid(self):
        '''
        Returns the tuple of lon and lat
        position.
        '''
        centroid = self.get_geometry().centroid
        lon = centroid.x
        lat = centroid.y
        return lon, lat

    def get_taxonomies(self):
        '''
        Returns the list of taxonomies.
        '''
        return self._taxonomies

    def without_taxonomies(self, schema=None):
        '''
        New cell with the same name and geometry
        but without the taxonomy data.
        '''
        if schema is None:
            schema = self._schema
        return ExposureCell(
            schema=schema,
            gid=self._gid,
            name=self._name,
            geometry=self._geometry,
            taxonomies=[]
        )

    def add_taxonomy(self, taxonomy):
        '''
        Adds one taxonomy dataset.
        Here is logic to merge with taxonomies that are
        already included.
        '''

        idx_to_insert = None
        for idx, test_tax in enumerate(self._taxonomies):
            if taxonomy.can_be_merged(test_tax):
                idx_to_insert = idx

        if idx_to_insert is not None:
            self._taxonomies[idx_to_insert].merge(taxonomy)
        else:
            self._taxonomies.append(taxonomy)

    def update_single_taxonomy(
            self,
            taxonomy_bag,
            intensity_with_units,
            fragility_provider,
            transition_cell):
        '''
        Updates the cell with a given taxonomy,
        intensities and fragility functions.
        Also updates the transition cell.
        '''
        taxonomy = taxonomy_bag.get_taxonomy()
        old_damage_state = taxonomy_bag.get_damage_state()

        intensity, units = intensity_with_units

        damage_states_to_care = get_sorted_damage_states(
            fragility_provider,
            taxonomy,
            old_damage_state
        )

        n_left = taxonomy_bag.get_n_buildings()

        for single_damage_state in damage_states_to_care:
            probability = single_damage_state.get_probability_for_intensity(
                intensity,
                units
            )

            n_buildings_in_damage_state = probability * n_left

            n_left -= n_buildings_in_damage_state

            self.add_taxonomy(
                taxonomy_bag.with_updated_mapping(
                    schema=taxonomy_bag.get_schema(),
                    taxonomy=taxonomy,
                    damage_state=single_damage_state.to_state,
                    n_buildings=n_buildings_in_damage_state
                )
            )
            if n_buildings_in_damage_state > 0:
                transition_cell.add_transition(
                    transition.Transition(
                        schema=taxonomy_bag.get_schema(),
                        taxonomy=taxonomy,
                        from_damage_state=single_damage_state.from_state,
                        to_damage_state=single_damage_state.to_state,
                        n_buildings=n_buildings_in_damage_state
                    )
                )
        if n_left > 0:
            self.add_taxonomy(
                taxonomy_bag.with_updated_mapping(
                    schema=taxonomy_bag.get_schema(),
                    taxonomy=taxonomy,
                    damage_state=taxonomy_bag.get_damage_state(),
                    n_buildings=n_left
                )
            )

    def update(self, intensity_provider, fragility_provider):
        '''
        Returns a new cell with the updated damage states
        and a cell with the transitions.
        '''
        lon, lat = self.get_lon_lat_of_centroid()
        intensity_with_units = intensity_provider.get_nearest(lon=lon, lat=lat)

        updated_cell = self.without_taxonomies()
        transition_cell = transition.TransitionCell.from_exposure_cell(
            updated_cell
        )

        for taxonomy_bag in self._taxonomies:
            updated_cell.update_single_taxonomy(
                taxonomy_bag,
                intensity_with_units,
                fragility_provider,
                transition_cell,
            )
        return updated_cell, transition_cell

    def map_schema(self, target_schema, schema_mapper):
        '''
        Returns an exposure cell mapped into a different
        schema.
        '''
        mapped_cell = self.without_taxonomies(schema=target_schema)

        for taxonomy_bag in self.get_taxonomies():
            taxonomy = taxonomy_bag.get_taxonomy()
            damage_state = taxonomy_bag.get_damage_state()
            n_buildings = taxonomy_bag.get_n_buildings()

            mapping_results = schema_mapper.map_schema(
                source_taxonomy=taxonomy,
                source_damage_state=damage_state,
                source_schema=self._schema,
                target_schema=target_schema,
                n_buildings=n_buildings
            )

            for res in mapping_results:
                new_taxonomy_bag = taxonomy_bag.with_updated_mapping(
                    schema=target_schema,
                    taxonomy=res.get_taxonomy(),
                    damage_state=res.get_damage_state(),
                    n_buildings=res.get_n_buildings()
                )
                mapped_cell.add_taxonomy(new_taxonomy_bag)
        return mapped_cell

    @classmethod
    def from_simple_series(cls, schema, series):
        '''
        Read the exposure cell from a simple series.
        '''
        gid = series['gc_id']
        name = series['name']
        geometry = series['geometry']

        taxonomies = []

        keys_without_tax = set(['gc_id', 'name', 'geometry', 'index'])

        for key in series.keys():
            if key not in keys_without_tax:
                taxonomy_bag = TaxonomyDataBag.from_simple_series(
                    schema=schema,
                    series=series,
                    key=key
                )
                taxonomies.append(taxonomy_bag)
        return cls(
            schema=schema,
            gid=gid,
            name=name,
            geometry=geometry,
            taxonomies=taxonomies
        )

    def to_simple_series(self):
        '''
        Converts the exposure cell into a simple pandas
        series.
        '''
        series = pd.Series({
            'gc_id': self._gid,
            'name': self._name,
            'geometry': self._geometry,
        })

        for taxonomy_bag in self._taxonomies:
            key = taxonomy_bag.get_taxonomy() + \
                    '_D' + \
                    str(taxonomy_bag.get_damage_state())
            series[key] = taxonomy_bag.get_n_buildings()

        return series

    def to_series(self):
        '''
        Converts the exposure cell into a more complex
        series structure with a table like appoach for
        displaying the taxonomies, the damage states
        and the affected buildings.
        '''
        series = pd.Series({
            'gid': self._gid,
            'name': self._name,
            'geometry': self._geometry,
            'expo': {
                'Taxonomy': [x.get_taxonomy() for x in self._taxonomies],
                'Damage': [
                    'D' + str(x.get_damage_state())
                    for x in self._taxonomies
                ],
                'Buildings': [x.get_n_buildings() for x in self._taxonomies],
                'id': [x.get_area_id() for x in self._taxonomies],
                'Region': [x.get_region() for x in self._taxonomies],
                'Dwellings': [x.get_dwellings() for x in self._taxonomies],
                'Repl-cost-USD-bdg': [
                    x.get_repl_cost_usd_bdg()
                    for x in self._taxonomies
                ],
                'Population': [x.get_population() for x in self._taxonomies],
                'name': [x.get_name() for x in self._taxonomies],
            }
        })
        return series

    @classmethod
    def from_series(cls, schema, series):
        '''
        Reads the exposure cell from a more complex series structure
        with a table like approach in the expo field to
        store taxonomies, damage states and the number of buildings.
        '''
        gid = series['gid']
        name = series['name']
        geometry = series['geometry']
        expo = pd.DataFrame(series['expo'])

        taxonomies = []

        for _, taxonomy_dataset in expo.iterrows():
            taxonomy_bag = TaxonomyDataBag.from_series(
                schema=schema,
                series=taxonomy_dataset
            )
            taxonomies.append(taxonomy_bag)

        return cls(
            schema=schema,
            gid=gid,
            name=name,
            geometry=geometry,
            taxonomies=taxonomies
        )


class TaxonomyDataBag():
    '''
    Data structure to store the taxonomy, the schema,
    the damage state, the number of buildings and some other
    data.
    '''
    def __init__(
            self,
            schema,
            taxonomy,
            damage_state,
            n_buildings,
            area_id=None,
            region=None,
            dwellings=None,
            repl_cost_usd_bdg=None,
            population=None,
            name=None):
        self._schema = schema
        self._taxonomy = taxonomy
        self._damage_state = damage_state
        self._n_buildings = n_buildings

        if math.isnan(self._n_buildings):
            self._n_buildings = 0.0

        self._area_id = area_id
        self._region = region
        self._dwellings = dwellings
        self._repl_cost_usd_bdg = repl_cost_usd_bdg
        self._population = population
        self._name = name

    def with_updated_mapping(
            self,
            schema,
            taxonomy,
            damage_state,
            n_buildings):
        '''
        Returns a copy of this data but with updated
        schema, taxonomy, damage state and number of buildings.
        '''
        return TaxonomyDataBag(
            schema=schema,
            taxonomy=taxonomy,
            damage_state=damage_state,
            n_buildings=n_buildings,
            area_id=self._area_id,
            region=self._region,
            dwellings=self._dwellings,
            repl_cost_usd_bdg=self._repl_cost_usd_bdg,
            population=self._population,
            name=self._name
        )

    def get_schema(self):
        '''
        Returns the schema.
        '''
        return self._schema

    def get_taxonomy(self):
        '''
        Returns the taxonomy.
        '''
        return self._taxonomy

    def get_damage_state(self):
        '''
        Returns the damage state.
        '''
        return self._damage_state

    def get_n_buildings(self):
        '''
        Returns the number of buildings.
        '''
        return self._n_buildings

    def get_area_id(self):
        '''
        Returns the area id data.
        '''
        return self._area_id

    def get_region(self):
        '''
        Returns the region.
        '''
        return self._region

    def get_dwellings(self):
        '''
        Returns the dwellings.
        '''
        return self._dwellings

    def get_repl_cost_usd_bdg(self):
        '''
        Returns the replacement costs in usd per building.
        '''
        return self._repl_cost_usd_bdg

    def get_population(self):
        '''
        Returns the population of the cell.
        '''
        return self._population

    def get_name(self):
        '''
        Returns the name of the cell.
        '''
        return self._name

    def can_be_merged(self, other_taxonomy):
        '''
        Tests if two taxonomy data bags for the same
        cell can be merged.
        '''
        if self._schema != other_taxonomy.get_schema():
            return False
        if self._taxonomy != other_taxonomy.get_taxonomy():
            return False
        if self._damage_state != other_taxonomy.get_damage_state():
            return False
        return True

    def merge(self, other_taxonomy):
        '''
        Adds the number of buildings.
        Here is no check if the other taxonomy data bag
        can be merged or not.
        Use the can_be_merged method before.
        '''
        self._n_buildings += other_taxonomy.get_n_buildings()

    @classmethod
    def from_series(cls, series, schema):
        '''
        Reads the taxonomy data bag from a series.
        '''
        return cls(
            schema=schema,
            taxonomy=series['Taxonomy'],
            damage_state=remove_prefix_d_for_damage_state(series['Damage']),
            n_buildings=series['Buildings'],
            area_id=series['id'],
            region=series['Region'],
            dwellings=series['Dwellings'],
            repl_cost_usd_bdg=series['Repl-cost-USD-bdg'],
            population=series['Population'],
            name=series['name']
        )

    @classmethod
    def from_simple_series(cls, series, key, schema):
        '''
        Reads the taxonomy data bag from a simple series.
        '''
        n_buildings = series[key]
        key = key.replace(r'\/', '/')
        damage_state = \
            extract_damage_state_from_taxonomy_damage_state_string(key)

        return cls(
            schema=schema,
            taxonomy=extract_taxonomy_from_taxonomy_damage_state_string(key),
            damage_state=damage_state,
            n_buildings=n_buildings,
            name=series['name']
        )


def remove_prefix_d_for_damage_state(damage_state_with_prefix_d):
    '''
    Removes a prefix d before a damage state number.
    '''
    match = re.search(r'^D?(\d+)', damage_state_with_prefix_d)
    return int(match.group(1))


def extract_taxonomy_from_taxonomy_damage_state_string(
        tax_damage_state_string):
    '''
    Extracts the taxonomy from a string with first the taxonomy and
    then the damage state (W_D3 for example).
    '''
    return re.sub(r'_D(\d+)$', '', tax_damage_state_string)


def extract_damage_state_from_taxonomy_damage_state_string(
        tax_damage_state_string):
    '''
    Extracts the damage state from a string with first the taxonomy
    and then the damage state (W_D3 for example).
    Returns 0 if there is no explicit damage state.
    '''
    match = re.search(r'_D(\d+)$', tax_damage_state_string)
    if match:
        return int(match.group(1))
    return 0


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
