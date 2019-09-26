#!/usr/bin/env python3




'''
Rethink: What does both have in common?

- I have a list of cells
- I have a name, a gid, and a geometry for all of them

- then I have a list of taxonomies
  * in the old one this is just the name of the taxonomy,
    the damage state and the numbers
  * in the new one I have region, the taxonomy, the dwellings, the buildings (so n),
    the repl_cost, the population, the name of the region, and the damage state



'''
import math
import re

import pandas as pd
import geopandas as gpd


class ExposureCellList():
    def __init__(self, exposure_cells):
        self._exposure_cells = exposure_cells

    def get_exposure_cells(self):
        return self._exposure_cells

    def append(self, exposure_cell):
        self._exposure_cells.append(exposure_cell)

    def map_schema(self, target_schema, schema_mapper):
        elements = []
        for exposure_cell in self._exposure_cells:
            mapped_cell = exposure_cell.map_schema(target_schema, schema_mapper)
            elements.append(mapped_cell)
        return ExposureCellList(elements)
        

    @classmethod
    def from_dataframe(cls, schema, dataframe):
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
        gdf = gpd.GeoDataFrame.from_file(file_name)
        if 'expo' in gdf.columns:
            return cls.from_dataframe(schema, gdf)
        return cls.from_simple_dataframe(schema, gdf)


    def to_simple_dataframe(self):
        series = [x.to_simple_series() for x in self._exposure_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])

    def to_dataframe(self):
        series = [x.to_series() for x in self._exposure_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])

class ExposureCell():
    def __init__(self, schema, gid, name, geometry, taxonomies):
        self._schema = schema
        self._gid = gid
        self._name = name
        self._geometry = geometry
        self._taxonomies = taxonomies

    def get_schema(self):
        return self._schema

    def get_gid(self):
        return self._gid

    def get_name(self):
        return self._name

    def get_geometry(self):
        return self._geometry

    def get_lon_lat_of_centroid(self):
        centroid = self.get_geometry()
        lon = centroid.x
        lat = centroid.y
        return lon, lat

    def get_taxonomies(self):
        return self._taxonomies

    def without_taxonomies(self, schema=None):
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

        idx_to_insert = None
        for idx, test_tax in enumerate(self._taxonomies):
            if taxonomy.can_be_merged(test_tax):
                idx_to_insert = idx

        if idx_to_insert is not None:
            self._taxonomies[idx].merge(taxonomy)
        else:
            self._taxonomies.append(taxonomy)

    def update_single_taxonomy(self, taxonomy_bag, intensity_with_units, fragility_provider, transition_cell):
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
                    Transition(
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
        lon, lat = self.get_lon_lat_of_centroid()
        intensity_with_units = intensity_provider.get_nearest(lon=lon, lat=lat)

        updated_cell = self.without_taxonomies()
        transition_cell = TransitionCell.from_exposure_cell(updated_cell)

        for taxonomy_bag in self._taxonomies:
            updated_cell.update_single_taxonomy(
                taxonomy_bag,
                intensity_with_units,
                fragility_provider,
                transition_cell,
            )
        return updated_cell, transition_cell

    def map_schema(self, target_schema, schema_mapper):
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
        series = pd.Series({
            'gc_id': self._gid,
            'name': self._name,
            'geometry': self._geometry,
        })

        for taxonomy_bag in self._taxonomies:
            key = taxonomy_bag.get_taxonomy() + '_D' + str(taxonomy_bag.get_damage_state())
            series[key] = taxonomy_bag.get_n_buildings()

        return series

    def to_series(self):
        series = pd.Series({
            'gid': self._gid,
            'name': self._name,
            'geometry': self._geometry,
            'expo': {
                'Taxonomy': [x.get_taxonomy() for x in self._taxonomies],
                'Damage': ['D' + str(x.get_damage_state()) for x in self._taxonomies],
                'Buildings': [x.get_n_buildings() for x in self._taxonomies],
                'id': [x.get_area_id() for x in self._taxonomies],
                'Region': [x.get_region() for x in self._taxonomies],
                'Dwellings': [x.get_dwellings() for x in self._taxonomies],
                'Repl_cost_USD/bdg': [x.get_repl_cost_usd_bdg() for x in self._taxonomies],
                'Population': [x.get_population() for x in self._taxonomies],
                'name': [x.get_name() for x in self._taxonomies],
            }
        })
        return series


    @classmethod
    def from_series(cls, schema, series):
        gid = series['gid']
        name = series['name']
        geometry = series['geometry']
        expo = pd.DataFrame(series['expo'])

        taxonomies = []

        for _, taxonomy_dataset in expo.iterrows():
            taxonomy_bag = TaxonomyDataBag.from_series(schema=schema, series=taxonomy_dataset)
            taxonomies.append(taxonomy_bag)

        return cls(
            schema=schema,
            gid=gid,
            name=name,
            geometry=geometry,
            taxonomies=taxonomies
        )

class TaxonomyDataBag():
    def __init__(self, 
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

    def with_updated_mapping(self, schema, taxonomy, damage_state, n_buildings):
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
        return self._schema
    def get_taxonomy(self):
        return self._taxonomy
    def get_damage_state(self):
        return self._damage_state
    def get_n_buildings(self):
        return self._n_buildings
    def get_area_id(self):
        return self._area_id
    def get_region(self):
        return self._region
    def get_dwellings(self):
        return self._dwellings
    def get_repl_cost_usd_bdg(self):
        return self._repl_cost_usd_bdg
    def get_population(self):
        return self._population
    def get_name(self):
        return self._name

    def can_be_merged(self, other_taxonomy):
        if self._schema != other_taxonomy.get_schema():
            return False
        if self._taxonomy != other_taxonomy.get_taxonomy():
            return False
        if self._damage_state != other_taxonomy.get_damage_state():
            return False
        return True

    def merge(self, other_taxonomy):
        self._n_buildings += other_taxonomy.get_n_buildings()

    @classmethod
    def from_series(cls, series, schema):
        return cls(
            schema=schema,
            taxonomy = series['Taxonomy'],
            damage_state=remove_prefix_d_for_damage_state(series['Damage']),
            n_buildings=series['Buildings'],
            area_id=series['id'],
            region=series['Region'],
            dwellings=series['Dwellings'],
            repl_cost_usd_bdg=series['Repl_cost_USD/bdg'],
            population=series['Population'],
            name=series['name']
        )

    @classmethod
    def from_simple_series(cls, series, key, schema):
        n_buildings=series[key]
        key = key.replace(r'\/', '/')
        return cls(
            schema=schema,
            taxonomy=extract_taxonomy_from_taxonomy_damage_state_string(key),
            damage_state=extract_damage_state_from_taxonomy_damage_state_string(key),
            n_buildings=n_buildings,
            name=series['name']
        )

class TransitionCell():
    def __init__(self, schema, gid, name, geometry, transitions):
        self._schema = schema
        self._gid = gid
        self._name = name
        self._geometry = geometry
        self._transitions = transitions

    def get_schema(self):
        return self._schema

    def get_gid(self):
        return self._gid
    
    def get_name(self):
        return self._name

    def get_geometry(self):
        return self._geometry

    def get_transitions(self):
        return self._transitions

    def add_transition(self, transition):
        idx_to_add = None

        for idx, single_transition in enumerate(self._transitions):
            if single_transition.can_be_merged(transition):
                idx_to_add = idx

        if idx_to_add is not None:
            self._transitions[idx_to_add].merge(transition)
        else:
            self._transitions.append(transition)

    def to_series(self):
        series = pd.Series({
            'gid': self._gid,
            'name': self._name,
            'geometry': self._geometry,
            'schema': self._schema,
            'transitions': {
                'taxonomy': [x.get_taxonomy() for x in self._transitions],
                'from_damage_state': [x.get_from_damage_state() for x in self._transitions],
                'to_damage_state': [x.get_to_damage_state() for x in self._transitions],
                'n_buildings': [x.get_n_buildings() for x in self._transitions],
            },
        })
        return series


    @classmethod
    def from_exposure_cell(cls, exposure_cell):
        return cls(
            schema = exposure_cell.get_schema(),
            gid = exposure_cell.get_gid(),
            name = exposure_cell.get_name(),
            geometry = exposure_cell.get_geometry(),
            transitions = []
        )

class Transition():
    def __init__(self, schema, taxonomy, from_damage_state, to_damage_state, n_buildings):
        self._schema = schema
        self._taxonomy = taxonomy
        self._from_damage_state = from_damage_state
        self._to_damage_state = to_damage_state
        self._n_buildings = n_buildings

    def get_schema(self):
        return self._schema

    def get_taxonomy(self):
        return self._taxonomy

    def get_from_damage_state(self):
        return self._from_damage_state

    def get_to_damage_state(self):
        return self._to_damage_state

    def get_n_buildings(self):
        return self._n_buildings

    def can_be_merged(self, other_transition):
        if self._schema != other_transition.get_schema():
            return False
        if self._taxonomy != other_transition.get_taxonomy():
            return False
        if self._from_damage_state != other_transition.get_from_damage_state():
            return False
        if self._to_damage_state != other_transition.get_to_damage_state():
            return False
        return True

    def merge(self, other_transition):
        self._n_buildings += other_transition.get_n_buildings()

class TransitionCellList():
    def __init__(self, transition_cells):
        self._transition_cells = transition_cells

    def get_transition_cells(self):
        return self._transition_cells

    def append(self, transition_cell):
        self._transition_cells.append(transition_cell)

    def to_dataframe(self):
        series = [x.to_series() for x in self._transition_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])

class LossCellList():
    def __init__(self, loss_cells):
        self._loss_cells = loss_cells

    def get_loss_cells(self):
        return self._loss_cells

    def append(self, loss_cell):
        self._loss_cells.append(loss_cell)

    def to_dataframe(self):
        series = [x.to_series() for x in self._loss_cells]
        dataframe = pd.DataFrame(series)
        return gpd.GeoDataFrame(dataframe, geometry=dataframe['geometry'])


class LossCell():
    def __init__(self, gid, name, geometry, loss_value, loss_unit):
        self._gid = gid
        self._name = name
        self._geometry = geometry
        self._loss_value = loss_value
        self._loss_unit = loss_unit

    def get_gid(self):
        return self._gid
    
    def get_name(self):
        return self._name

    def get_geometry(self):
        return self._geometry

    def get_loss_value(self):
        return self._loss_value

    def get_loss_unit(self):
        return self._loss_unit

    def to_series(self):
        series = pd.Series({
            'gid': self._gid,
            'name': self._name,
            'geometry': self._geometry,
            'loss_value': self._loss_value,
            'loss_unit': self._loss_unit,
        })
        return series

    @classmethod
    def from_transition_cell(cls, transition_cell, loss_provider):
        loss_value = 0

        for transition in transition_cell.get_transitions():
            single_loss_value = loss_provider.get_loss(
                schema=transition_cell.get_schema(),
                taxonomy=transition.get_taxonomy(),
                from_damage_state=transition.get_from_damage_state(),
                to_damage_state=transition.get_to_damage_state()
            )
            n_loss_value = single_loss_value * transition.get_n_buildings()

            loss_value += n_loss_value

        return cls(
            gid=transition_cell.get_gid(),
            name=transition_cell.get_name(),
            geometry=transition_cell.get_geometry(),
            loss_value=loss_value,
            loss_unit=loss_provider.get_unit()
        )


def remove_prefix_d_for_damage_state(damage_state_with_prefix_d):
    match = re.search(r'^D?(\d+)', damage_state_with_prefix_d)
    return int(match.group(1))

def extract_taxonomy_from_taxonomy_damage_state_string(tax_damage_state_string):
    return re.sub(r'_D(\d+)$', '', tax_damage_state_string)

def extract_damage_state_from_taxonomy_damage_state_string(tax_damage_state_string):
    match = re.search(r'_D(\d+)$', tax_damage_state_string)
    if match:
        return int(match.group(1))
    return 0

def get_sorted_damage_states(
        fragility_provider,
        taxonomy,
        old_damage_state):

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
