#!/usr/bin/env python3

"""Script to create a shapefile out of a geojson."""

import json
import os
import sys

import geopandas
import numpy
import pandas
import shapely


class CustomColumnGenerator:
    """
    Generator for custom columns.

    Shapefile column names are very limited so we create c1, c2, ...
    and provide information to store the "real" names of those
    columns somewhere else.
    """

    def __init__(self, prefix):
        """Init the generator with a prefix."""
        self.prefix = prefix
        self.count = 1
        self.custom_column_names = {}
        self.custom_cols = {}

    def set_value_for_custom_column(self, long_name, id, value):
        """
        Set the value for a custom column.

        We use the id as mabye not all the rows have an entry
        for the specific custom column.
        """
        if long_name in self.custom_column_names.keys():
            col_name = self.custom_column_names[long_name]
        else:
            col_name = self._create_new_col()
            self.custom_column_names[long_name] = col_name
        self.custom_cols.setdefault(col_name, {})
        self.custom_cols[col_name][id] = value

    def _create_new_col(self):
        """Generate a new column name and increase the counter."""
        col_name = f"{self.prefix}{self.count}"
        self.count += 1
        return col_name

    def full_columns(self, id_array):
        """Return a dict with full lists for all the custom columns."""
        results = {}
        for col_name, value_dict_by_id in self.custom_cols.items():
            results[col_name] = []
            for id in id_array:
                results[col_name].append(self.custom_cols[col_name].get(id))
        return results

    def get_custom_column_mapping(self):
        """Return the mapping of the long names to the custom names."""
        return {v: k for k, v in self.custom_column_names.items()}


def compute_mean_transition(transitions_dict):
    """
    Compute the mean transitions.

    Pseudo-code was provided by Michael Langbein (DLR).
    """
    n_buildings = numpy.array(transitions_dict["n_buildings"])
    from_damage_state = numpy.array(transitions_dict["from_damage_state"])
    to_damage_state = numpy.array(transitions_dict["to_damage_state"])
    if len(n_buildings) == 0:
        return 0

    mean_damage_state_diff = (
        n_buildings * to_damage_state - n_buildings * from_damage_state
    ).mean()
    return mean_damage_state_diff


def dx_to_int(ds):
    """Transform a D3 to 3."""
    return int(ds[1:])


def compute_weighted_damage(expo_dict):
    """
    Compute the weighted damage.

    Pseudo-code was provided by Michael Langbein (DLR).
    """
    buildings = numpy.array(expo_dict["Buildings"])
    damage_raw = [dx_to_int(x) for x in expo_dict["Damage"]]
    damage = numpy.array(damage_raw)
    buildings_sum = buildings.sum()
    if buildings_sum != 0:
        weighted_damage = (buildings * damage).sum() / buildings.sum()
    else:
        weighted_damage = 0
    return weighted_damage


def main():
    """Run the main function to create a shapefile."""
    if len(sys.argv) < 2:
        print(
            "Usage python3 create_shapefile.py <jsonfile>",
            file=sys.stderr,
        )
        exit(1)
    filename_json_in = sys.argv[1]

    with open(filename_json_in) as infile:
        data_in = json.load(infile)

    ids = []
    geometries = []
    # The loss value is one of the main components for the visualization
    loss_values = []
    # Another one is the mean transiton value
    mean_transitions = []
    # And the weighted damage
    weighted_damages = []

    loss_unit = None
    custom_cols = CustomColumnGenerator(prefix="c")

    for feature in data_in["features"]:
        properties = feature["properties"]
        gid = properties["gid"]
        ids.append(gid)

        json_geometry = feature["geometry"]
        geometry = shapely.geometry.shape(json_geometry)
        geometries.append(geometry)

        loss_values.append(properties["loss_value"])
        if loss_unit is None and properties["loss_unit"]:
            loss_unit = properties["loss_unit"]

        transitions_dict = properties["transitions"]
        expo_dict = properties["expo"]
        mean_transitions.append(compute_mean_transition(transitions_dict))
        weighted_damages.append(compute_weighted_damage(expo_dict))
        # Next is to create transition matrix
        matrix = {}
        for from_ds, to_ds, n in zip(
            transitions_dict["from_damage_state"],
            transitions_dict["to_damage_state"],
            transitions_dict["n_buildings"],
        ):
            matrix.setdefault(from_ds, {})
            matrix[from_ds].setdefault(to_ds, 0)
            matrix[from_ds][to_ds] += n
        for k, v in matrix.items():
            custom_col_long_name = f"Transitions from damage state {k}"
            custom_col_value = json.dumps(v)
            custom_cols.set_value_for_custom_column(
                long_name=custom_col_long_name,
                id=gid,
                value=custom_col_value,
            )

        # After that we want to store the buildings per tax & damage state
        buildings_by_tax_and_ds = {}
        for taxonomy, damage, number in zip(
            expo_dict["Taxonomy"],
            expo_dict["Damage"],
            expo_dict["Buildings"],
        ):
            damage = dx_to_int(damage)
            buildings_by_tax_and_ds.setdefault(taxonomy, {})
            buildings_by_tax_and_ds[taxonomy].setdefault(damage, {})
            buildings_by_tax_and_ds[taxonomy][damage] = number
        for (
            taxonomy,
            buildings_by_ds,
        ) in buildings_by_tax_and_ds.items():
            custom_col_long_name = f"Buildings in {taxonomy} per damage state"
            custom_col_value = json.dumps(buildings_by_ds)
            custom_cols.set_value_for_custom_column(
                long_name=custom_col_long_name,
                id=gid,
                value=custom_col_value,
            )

    df = pandas.DataFrame(
        {
            "id": ids,
            "loss_value": loss_values,
            "m_tran": mean_transitions,
            "w_damage": weighted_damages,
            **custom_cols.full_columns(ids),
        }
    )
    gdf = geopandas.GeoDataFrame(df, geometry=geometries)
    gdf.crs = {"init": "EPSG:4326"}

    for ending in ["shp", "cpg", "dbf", "prj", "shx"]:
        filename = "summary." + ending
        if os.path.exists(filename):
            os.unlink(filename)

    gdf.to_file("summary.shp")

    with open("meta_summary.json", "w") as outfile:
        json.dump(
            {
                "custom_columns": custom_cols.get_custom_column_mapping(),
                "loss_unit": loss_unit,
            },
            outfile,
        )


if __name__ == "__main__":
    main()
