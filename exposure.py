#!/usr/bin/env python3

'''
Module for handling the exposure data.
'''

import math
import re

import pandas as pd
import geopandas as gpd


class ExposureCellProvider():
    '''
    Class to give access to all of the
    exposure cells.
    '''
    def __init__(self, gdf, schema):
        self._gdf = gdf
        self._schema = schema

    def __iter__(self):
        for _, row in self._gdf.iterrows():
            yield ExposureCell(row, self._schema)

    @classmethod
    def from_file(cls, file_name, schema):
        '''
        Read the data from a file.
        '''
        gdf = gpd.GeoDataFrame.from_file(file_name)
        return cls(gdf, schema)


class ExposureCellCollector():
    '''
    Class to collection all the (updated) exposure cells.
    Used for output.
    '''
    def __init__(self):
        self._elements = []

    def append(self, exposure_cell):
        '''
        Appends an exposure cell.
        '''
        self._elements.append(exposure_cell)

    def __str__(self):
        gdf = gpd.GeoDataFrame([x.get_series() for x in self._elements])
        return gdf.to_json()


class ExposureCell():
    '''
    Class to represent an exposure cell.
    '''
    def __init__(self, series, schema):
        self._series = series
        self._schema = schema

    def get_series(self):
        '''
        Just returns the series as it is.
        '''
        return self._series

    def get_schema(self):
        return self._schema

    def get_lon_lat_of_centroid(self):
        '''
        Returns the longitude and latitude of
        the geometry as a tuple.
        '''
        geometry = self._series['geometry']
        centroid = geometry.centroid
        lon = centroid.x
        lat = centroid.y

        return lon, lat

    def new_prototype(self, schema):
        '''
        Creates a new exposure cell that contains
        the same name and geometry as the base object,
        but has no data about the count of buildings for
        a taxonomy.
        '''
        series = pd.Series()
        for field in ExposureCell.get_fields_to_copy():
            series[field] = self._series[field]
        return ExposureCell(series, schema)

    def new_transition_cell(self):
        series = pd.Series()
        for field in ExposureCell.get_fields_to_copy():
            series[field] = self._series[field]
        return TransitionCell(series)

    def get_taxonomies(self):
        '''
        Returns all of the taxonomies that are given for the
        exposure cell.
        '''
        result = []
        for field in self._series.keys():
            if field not in ExposureCell.get_fields_to_copy():
                if field not in ExposureCell.get_fields_to_ignore():
                    count = self._series[field]
                    if math.isnan(count):
                        count = 0.0
                    name = field.replace(r'\/', '/')
                    result.append(Taxonomy(name=name, count=count, schema=self._schema))
        return result

    @staticmethod
    def get_fields_to_copy():
        '''
        Returns the names of fields that should be copied
        on creating a new exposure cell object.
        '''
        return 'name', 'geometry', 'gc_id'

    @staticmethod
    def get_fields_to_ignore():
        '''
        Returns the names of fields that should be ignored
        on searching for the taxonomy fields.
        '''
        return 'index', 'id'

    def add_n_for_damage_state(self, exposure_taxonomy, damage_state, count):
        '''
        Adds the number of buildings for the given taxonomy
        and the given new damage state.
        '''
        exposure_to_set = update_taxonomy_damage_state(
            exposure_taxonomy, damage_state)
        if exposure_to_set not in self._series.keys():
            self._series[exposure_to_set] = 0.0
        self._series[exposure_to_set] += count

    def map_schema(self,
            target_name,
            schema_mapper):
        mapped_cell = self.new_prototype(target_name)

        for taxonomy in self.get_taxonomies():
            building_class = taxonomy.get_building_class()
            damage_state = taxonomy.get_damage_state()
            count = taxonomy.get_count()

            mapping_results = schema_mapper.map_schema(
                source_building_class=building_class,
                source_damage_state=damage_state,
                source_name=self._schema,
                target_name=target_name,
                n_buildings=count
            )

            for res in mapping_results:
                mapped_cell.add_n_for_damage_state(
                        res.get_building_class(),
                        res.get_damage_state(),
                        res.get_n_buildings(),
                )
        return mapped_cell


    def _update_taxonomy(self, old_taxonomy, intensity, units, fragility_provider, transition_cell):
        building_class = old_taxonomy.get_building_class()
        old_damage_state = old_taxonomy.get_damage_state()
        old_count = old_taxonomy.get_count()

        damage_states = fragility_provider.get_damage_states_for_taxonomy(
            building_class)

        damage_states_to_care = [
            ds for ds in damage_states
            if ds.from_state == old_damage_state
            and ds.to_state > old_damage_state
        ]

        damage_states_to_care.sort(key=sort_by_to_damage_state_desc)

        n_left = old_count

        for single_damage_state in damage_states_to_care:
            probability = single_damage_state.get_probability_for_intensity(
                intensity, units)
            n_buildings_in_damage_state = probability * n_left

            n_left -= n_buildings_in_damage_state

            self.add_n_for_damage_state(
                building_class,
                single_damage_state.to_state,
                n_buildings_in_damage_state
            )

            transition_cell.add_n_for_damage_state(
                building_class,
                single_damage_state.from_state,
                single_damage_state.to_state,
                n_buildings_in_damage_state
            )

        self.add_n_for_damage_state(
            building_class,
            old_damage_state,
            n_left
        )

    def update(self,
            intensity_provider,
            fragility_provider):
        lon, lat = self.get_lon_lat_of_centroid()
        intensity, units = intensity_provider.get_nearest(lon=lon, lat=lat)

        updated_cell = self.new_prototype(self._schema)
        transiton_cell = self.new_transition_cell()

        for taxonomy in self.get_taxonomies():
            updated_cell._update_taxonomy(taxonomy, intensity, units, fragility_provider, transiton_cell)
        return updated_cell, transiton_cell

def sort_by_to_damage_state_desc(damage_state):
    return damage_state.to_state * -1

def update_taxonomy_damage_state(taxonomy, new_damage_state):
    '''
    Returns the new taxonomy name for the new damage state.
    For example from AA with new damage state 1 the result
    is AA_D1.
    For AA_D1 with new damage state 2 the result is
    AA_D2.
    '''
    match = re.search(r'_D\d$', taxonomy)
    if not match:
        return taxonomy + '_D' + str(new_damage_state)
    return re.sub(r'_D\d$', '_D' + str(new_damage_state), taxonomy)


def get_damage_state_from_taxonomy(taxonomy_str):
    '''
    Returns the damage state from a given taxonomy string.
    For example for 'AA' the result is 0.
    For 'AA_D1' the result is 1.
    '''

    match = re.search(r'D(\d)$', taxonomy_str)
    if match:
        return int(match.group(1))
    return 0

def get_building_class_from_taxonomy(taxonomy_str):
    return re.sub(r'_D\d+$', '', taxonomy_str)

class Taxonomy():
    '''
    Class to handle the taxonomy of the exposure.
    '''
    def __init__(self, name, count, schema):
        self._name = name
        self._count = count
        self._schema = schema

    def __eq__(self, other):
        if isinstance(other, Taxonomy):
            return self._name == other.get_name() and \
                    self._count == other.get_count() and \
                    self._schema == other.get_schema()
        return False

    def get_damage_state(self):
        '''
        Returns the damage state.
        '''
        return get_damage_state_from_taxonomy(self._name)

    def get_building_class(self):
        return get_building_class_from_taxonomy(self._name)

    def get_name(self):
        '''
        Returns the name of the taxonomy.
        '''
        return self._name

    def get_count(self):
        '''
        Returns the given count of buildings in this class so far.
        '''
        return self._count

    def get_schema(self):
        return self._schema

class TransitionCell():
    def __init__(self, series):
        self._series = series

    def get_series(self):
        return self._series

    def add_n_for_damage_state(self, building_class, from_damage_state, to_damage_state, n_buildings):
        if building_class not in self._series.keys():
            self._series[building_class] = list()
        self._series[building_class].append({
            'from': from_damage_state,
            'to': to_damage_state,
            'n_buildings': n_buildings,
        })

class TransitionCellCollector():
    def __init__(self):
        self._elements = []

    def append(self, transition_cell):
        self._elements.append(transition_cell)

    def __str__(self):
        gdf = gpd.GeoDataFrame([x.get_series() for x in self._elements])
        return gdf.to_json()
