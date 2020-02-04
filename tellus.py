#!/usr/bin/env python3

"""
Module for all the common elements for deus and volcanus.
Name comes from https://de.wikipedia.org/wiki/Tellus
"""

import glob
import json
import multiprocessing
import os

import exposure
import fragility
import intensityprovider
import loss
import schemamapping
import shakemap
import transition


class Child():
    """
    This is a tellus child class that represents
    a deus instance.
    """
    def __init__(
            self,
            intensity_provider,
            fragility_provider,
            exposure_cell_provider,
            loss_provider,
            args_with_output_paths):
        self.intensity_provider = intensity_provider
        self.fragility_provider = fragility_provider
        self.exposure_cell_provider = exposure_cell_provider
        self.loss_provider = loss_provider
        self.args_with_output_paths = args_with_output_paths

    def run(self):
        """
        All the work is done here.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))

        schema_mapper = create_schema_mapper(current_dir)

        updated_exposure_cells = exposure.ExposureCellList([])
        transition_cells = transition.TransitionCellList([])
        loss_cells = loss.LossCellList([])

        for original_exposure_cell in (
            self.exposure_cell_provider.exposure_cells
        ):
            mapped_exposure_cell = original_exposure_cell.map_schema(
                target_schema=self.fragility_provider.schema,
                schema_mapper=schema_mapper
            )
            single_updated_exposure_cell, single_transition_cell = \
                mapped_exposure_cell.update(
                    intensity_provider=self.intensity_provider,
                    fragility_provider=self.fragility_provider
                )

            updated_exposure_cells.append(single_updated_exposure_cell)
            transition_cells.append(single_transition_cell)

            loss_cells.append(
                loss.LossCell.from_transition_cell(
                    single_transition_cell,
                    self.loss_provider
                )
            )

        updated_exposure_cells_df = updated_exposure_cells.to_dataframe()
        transition_cells_df = transition_cells.to_dataframe()
        loss_cells_df = loss_cells.to_dataframe()

        with multiprocessing.Pool() as p:
            p.map(
                ResultWriter.write, [
                    ResultWriter(
                        self.args_with_output_paths.updated_exposure_output_file,
                        updated_exposure_cells_df),
                    ResultWriter(
                        self.args_with_output_paths.transition_output_file,
                        transition_cells_df),
                    ResultWriter(
                        self.args_with_output_paths.loss_output_file,
                        loss_cells_df),
                ]
            )


        # and merge all of them together
        for other_df in [transition_cells_df, loss_cells_df]:
            for column in other_df.columns:
                if column not in updated_exposure_cells_df.columns:
                    updated_exposure_cells_df[column] = other_df[column]

        ResultWriter(
            self.args_with_output_paths.merged_output_file,
            updated_exposure_cells_df
        ).write()


def create_schema_mapper(current_dir):
    '''
    Creates and returns a schema mapper
    using local mapping files.
    '''
    pattern_to_search_for_tax_files = os.path.join(
        current_dir, 'schema_mapping_data_tax', '*.json')
    tax_mapping_files = glob.glob(pattern_to_search_for_tax_files)

    pattern_to_search_for_ds_files = os.path.join(
        current_dir, 'schema_mapping_data_ds', '*.json')
    ds_mapping_files = glob.glob(pattern_to_search_for_ds_files)

    return (schemamapping
            .SchemaMapper
            .from_taxonomy_and_damage_state_conversion_files(
                tax_mapping_files, ds_mapping_files))


class ResultWriter:
    '''
    This is a class to write results to files.
    '''
    def __init__(self, output_file, cells):
        self.output_file = output_file
        self.cells = cells

    def write(self):
        '''
        Write the updated exposure.
        '''
        if os.path.exists(self.output_file):
            os.unlink(self.output_file)
        self.cells.to_file(self.output_file, 'GeoJSON')

        # And because we want to reduce the size of the json files
        # as much possible, we will read them and wrote them without
        # any non necessary whitespace (to_file from geopandas
        # introduces some not needed whitespace).
        with open(self.output_file, 'rt') as read_handle:
            data = json.load(read_handle)
        with open(self.output_file, 'wt') as write_handle:
            json.dump(data, write_handle)
