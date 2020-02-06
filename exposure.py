#!/usr/bin/env python3

'''
Module for the exposure related classes.
'''

import collections
import math
import multiprocessing
import re

import pandas as pd
import geopandas as gpd

import transition


class ExposureCellList:
    '''
    List of exposure cells.
    '''
    def __init__(self, exposure_cells):
        self.exposure_cells = exposure_cells

    def append(self, exposure_cell):
        '''
        Appends an exposure cell.
        There is no logic to merge cells.
        '''
        self.exposure_cells.append(exposure_cell)

    def set_with_idx(self, idx, exposure_cell):
        '''
        Sets the exposure cell with an index.
        '''
        self.exposure_cells[idx] = exposure_cell

    def map_schema(self, target_schema, schema_mapper):
        '''
        Maps one whole list to a different schema.
        '''
        elements = [None] * len(self.exposure_cells)
        for idx, exposure_cell in enumerate(self.exposure_cells):
            mapped_cell = exposure_cell.map_schema(
                target_schema,
                schema_mapper
            )
            elements[idx] = mapped_cell
        return ExposureCellList(elements)

    @classmethod
    def from_dataframe(cls, schema, dataframe):
        '''
        Reads the list from a dataframe.
        '''
        elements = [None] * len(dataframe)
        mapper = RowMapping(schema)
        with multiprocessing.Pool() as p:
            mapping_results = p.map(mapper.map_row, dataframe.iterrows())

        for idx, exposure_cell in mapping_results:
            elements[idx] = exposure_cell
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
        series = [x.to_simple_series() for x in self.exposure_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])

    def to_dataframe(self):
        '''
        Converts the list to a dataframe with subdataframes
        for each cell (information about the taxonomies and
        the damage states seperated).
        '''
        series = [x.to_series() for x in self.exposure_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])


class ExposureCell:
    '''
    Spatial cell with the exposure data.
    '''
    def __init__(self, schema, gid, geometry, taxonomies):
        self.schema = schema
        self.gid = gid
        self.geometry = geometry
        self.taxonomies = taxonomies
        self._len_tax = len(taxonomies)

        self._tax_idx_by_taxonomy_key = {}
        for idx, taxonomy in enumerate(taxonomies):
            key = tb_to_key(taxonomy)
            self._tax_idx_by_taxonomy_key[key] = idx

    def get_lon_lat_of_centroid(self):
        '''
        Returns the tuple of lon and lat
        position.
        '''
        centroid = self.geometry.centroid
        lon = centroid.x
        lat = centroid.y
        return lon, lat

    def without_taxonomies(self, schema=None):
        '''
        New cell with the same geometry
        but without the taxonomy data.
        '''
        if schema is None:
            schema = self.schema
        return ExposureCell(
            schema=schema,
            gid=self.gid,
            geometry=self.geometry,
            taxonomies=[]
        )

    def add_taxonomy(self, taxonomy):
        '''
        Adds one taxonomy dataset.
        Here is logic to merge with taxonomies that are
        already included.
        '''
        key = tb_to_key(taxonomy)
        if key in self._tax_idx_by_taxonomy_key.keys():
            idx_to_insert = self._tax_idx_by_taxonomy_key.get(key)
            self.taxonomies[idx_to_insert]["n_buildings"] += \
                taxonomy["n_buildings"]
        else:
            new_idx = self._len_tax
            self._len_tax += 1
            # add a new object, not the reference
            self.taxonomies.append(taxonomy.copy())
            self._tax_idx_by_taxonomy_key[key] = new_idx

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
        basis_tb = taxonomy_bag.copy()

        taxonomy = taxonomy_bag["taxonomy"]
        old_damage_state = taxonomy_bag["damage_state"]

        intensity, units = intensity_with_units

        damage_states_to_care = get_sorted_damage_states(
            fragility_provider,
            taxonomy,
            old_damage_state
        )

        n_left = taxonomy_bag["n_buildings"]

        for single_damage_state in damage_states_to_care:
            probability = single_damage_state.get_probability_for_intensity(
                intensity,
                units
            )

            n_buildings_in_damage_state = probability * n_left

            n_left -= n_buildings_in_damage_state

            taxonomy_bag["taxonomy"] = taxonomy
            taxonomy_bag["damage_state"] = single_damage_state.to_state
            taxonomy_bag["n_buildings"] = n_buildings_in_damage_state

            self.add_taxonomy(taxonomy_bag)

            if n_buildings_in_damage_state > 0:
                transition_cell.add_transition(
                    transition.Transition(
                        schema=taxonomy_bag["schema"],
                        taxonomy=taxonomy,
                        from_damage_state=single_damage_state.from_state,
                        to_damage_state=single_damage_state.to_state,
                        n_buildings=n_buildings_in_damage_state
                    )
                )
        if n_left > 0:
            basis_tb["taxonomy"] = taxonomy
            basis_tb["n_buildings"] = n_left

            self.add_taxonomy(basis_tb)

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

        for taxonomy_bag in self.taxonomies:
            updated_cell.update_single_taxonomy(
                taxonomy_bag.copy(),
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

        for taxonomy_bag in self.taxonomies:
            taxonomy = taxonomy_bag["taxonomy"]
            damage_state = taxonomy_bag["damage_state"]
            n_buildings = taxonomy_bag["n_buildings"]

            mapping_results = schema_mapper.map_schema(
                source_taxonomy=taxonomy,
                source_damage_state=damage_state,
                source_schema=self.schema,
                target_schema=target_schema,
                n_buildings=n_buildings
            )

            for res in mapping_results:
                new_taxonomy_bag = taxonomy_bag.copy()

                new_taxonomy_bag["schema"] = target_schema
                new_taxonomy_bag["taxonomy"] = res.taxonomy
                new_taxonomy_bag["damage_state"] = res.damage_state
                new_taxonomy_bag["n_buildings"] = res.n_buildings

                mapped_cell.add_taxonomy(new_taxonomy_bag)
        return mapped_cell

    @classmethod
    def from_simple_series(cls, schema, series):
        '''
        Read the exposure cell from a simple series.
        '''
        gid = series['gc_id']
        geometry = series['geometry']

        taxonomies = []

        keys_without_tax = set(['gc_id', 'name', 'geometry', 'index'])

        for key in series.keys():
            if key not in keys_without_tax:
                taxonomy_bag = tb_from_simple_series(
                    schema=schema,
                    series=series,
                    key=key
                )
                taxonomies.append(taxonomy_bag)
        return cls(
            schema=schema,
            gid=gid,
            geometry=geometry,
            taxonomies=taxonomies
        )

    def to_simple_series(self):
        '''
        Converts the exposure cell into a simple pandas
        series.
        '''
        series = pd.Series({
            'gc_id': self.gid,
            'geometry': self.geometry,
        })

        for taxonomy_bag in self.taxonomies:
            key = taxonomy_bag["taxonomy"] + \
                    '_D' + \
                    str(taxonomy_bag["damage_state"])
            series[key] = taxonomy_bag["n_buildings"]

        return series

    def to_series(self):
        '''
        Converts the exposure cell into a more complex
        series structure with a table like appoach for
        displaying the taxonomies, the damage states
        and the affected buildings.
        '''
        series = pd.Series({
            'gid': self.gid,
            'geometry': self.geometry,
            'expo': {
                'Taxonomy': [x["taxonomy"] for x in self.taxonomies],
                'Damage': [
                    'D' + str(x["damage_state"])
                    for x in self.taxonomies
                ],
                'Buildings': [x["n_buildings"] for x in self.taxonomies],
                'id': [x["area_id"] for x in self.taxonomies],
                'Dwellings': [x["dwellings"] for x in self.taxonomies],
                'Repl-cost-USD-bdg': [
                    x["repl_cost_usd_bdg"]
                    for x in self.taxonomies
                ],
                'Population': [x["population"] for x in self.taxonomies],
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
        geometry = series['geometry']
        expo = pd.DataFrame(series['expo'])

        taxonomies = []

        for _, taxonomy_dataset in expo.iterrows():
            taxonomy_bag = tb_from_series(
                schema=schema,
                series=taxonomy_dataset
            )
            taxonomies.append(taxonomy_bag)

        return cls(
            schema=schema,
            gid=gid,
            geometry=geometry,
            taxonomies=taxonomies
        )


TaxonomyDataBagKey = collections.namedtuple(
    'TaxonomyDataBagKey',
    'schema taxonomy damage_state'
)


def tb_from_series(series, schema):
    '''
    Reads the taxonomy data bag from a series.
    '''
    n_buildings = series['Buildings']

    if math.isnan(n_buildings):
        n_buildings = 0.0

    return {
        "schema": schema,
        "taxonomy": series['Taxonomy'],
        "damage_state": remove_prefix_d_for_damage_state(series['Damage']),
        "n_buildings": n_buildings,
        "area_id": series['id'],
        "dwellings": series['Dwellings'],
        "repl_cost_usd_bdg": series['Repl-cost-USD-bdg'],
        "population": series['Population'],
    }


def tb_from_simple_series(series, key, schema):
    '''
    Reads the taxonomy data bag from a simple series.
    '''
    n_buildings = series[key]
    key = key.replace(r'\/', '/')
    damage_state = \
        extract_damage_state_from_taxonomy_damage_state_string(key)

    return {
        "schema": schema,
        "taxonomy": extract_taxonomy_from_taxonomy_damage_state_string(key),
        "damage_state": damage_state,
        "n_buildings": n_buildings,
    }


def tb_to_key(taxonomy_bag):
    return TaxonomyDataBagKey(
        taxonomy_bag["schema"],
        taxonomy_bag["taxonomy"],
        taxonomy_bag["damage_state"]
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


class RowMapping:
    '''
    This is a class used as a wrapper for multiprocessing
    mapping.
    '''
    def __init__(self, schema):
        self.schema = schema

    def map_row(self, idx_with_row):
        '''
        It takes a tuple of an index and the row
        and creates the exposure cell for the row
        (as given with enumerate(df.iterrows())).
        It returns the given index and the cell.
        '''
        idx, row = idx_with_row

        cell = ExposureCell.from_series(series=row, schema=self.schema)

        return idx, cell
