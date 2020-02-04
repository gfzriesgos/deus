#!/usr/bin/env python3

"""
Module for all the common elements for deus and volcanus.
Name comes from https://de.wikipedia.org/wiki/Tellus
"""

import collections
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
        # We use a multiprocessing pool here to work over the
        # cells in parallel (and write some output in parallel as well).
        with multiprocessing.Pool() as p:
            current_dir = os.path.dirname(os.path.realpath(__file__))

            schema_mapper = create_schema_mapper(current_dir)

            # Init the size of the lists for the cells.
            n_cells = len(self.exposure_cell_provider.exposure_cells)
            updated_exposure_cells = exposure.ExposureCellList(
                [None] * n_cells
            )
            transition_cells = transition.TransitionCellList(
                [None] * n_cells
            )
            loss_cells = loss.LossCellList(
                [None] * n_cells
            )

            # Map it in parallel.
            cell_mapper = CellMapper(self, schema_mapper)
            map_results = p.map(
                cell_mapper.map_cell,
                enumerate(self.exposure_cell_provider.exposure_cells)
            )

            # And collect the results & store them where they belong.
            # Note: We unpack the idx and the cells in for loop header.
            for idx, cells in map_results:
                updated_exposure_cells.set_with_idx(idx, cells.exposure_cell)
                transition_cells.set_with_idx(idx, cells.transition_cell)
                loss_cells.set_with_idx(idx, cells.loss_cell)

            # After we are done with the cells, we need to write them
            # to the filesystem.
            # This jobs write them out *AND* they return the cells as
            # geopandas dataframe (so that we can combine them and write
            # and additional output).
            # Instead of pure numerical indices we use strings here, so it may
            # be a bit cleaner where the values are from.
            parallel_write_and_convert_to_df_data = [
                IdxOutputFileAndCellsTuple(
                    'exposure',
                    self.args_with_output_paths.updated_exposure_output_file,
                    updated_exposure_cells
                ),
                IdxOutputFileAndCellsTuple(
                    'transitions',
                    self.args_with_output_paths.transition_output_file,
                    transition_cells
                ),
                IdxOutputFileAndCellsTuple(
                    'losses',
                    self.args_with_output_paths.loss_output_file,
                    loss_cells
                )
            ]
            parallel_write_and_convert_to_df_data_result = dict(
                p.map(
                    write_result_and_convert_to_df_tuple,
                    parallel_write_and_convert_to_df_data
                )
            )

            updated_exposure_cells_df = \
                parallel_write_and_convert_to_df_data_result['exposure']
            transition_cells_df = \
                parallel_write_and_convert_to_df_data_result['transitions']
            loss_cells_df = \
                parallel_write_and_convert_to_df_data_result['losses']

            # And now we merge the outputs together to a combined dataset, for
            # sending one file over the network in the riesgos demonstrator and
            # not having to send multiple ones.
            for other_df in [transition_cells_df, loss_cells_df]:
                for column in other_df.columns:
                    if column not in updated_exposure_cells_df.columns:
                        updated_exposure_cells_df[column] = other_df[column]

            write_result(
                self.args_with_output_paths.merged_output_file,
                updated_exposure_cells_df
            )


class CellMapper:
    '''
    This is class to support the parallel work with the
    exposure cells.
    Each map_cell call does the whole work (computing
    the updated exposure cell, the transitions and the
    loss).
    '''
    def __init__(self, tellus, schema_mapper):
        self.tellus = tellus
        self.schema_mapper = schema_mapper

    def map_cell(self, idx_with_original_exposure_cell):
        '''
        Computation of the updated exposure cell, the transition cell
        and the loss cell.
        As input it gets a tuple with the idx and the original exposure
        cell (as you get it with enumerate(original_exposure_cells)).

        The return value is a tuple of the original idx (to restore
        the very same order in later steps) and a triple with all
        of your real cells - updated exposure, transitions, losses.
        '''
        idx, original_exposure_cell = idx_with_original_exposure_cell

        mapped_exposure_cell = original_exposure_cell.map_schema(
            target_schema=self.tellus.fragility_provider.schema,
            schema_mapper=self.schema_mapper
        )
        single_updated_exposure_cell, single_transition_cell = \
            mapped_exposure_cell.update(
                intensity_provider=self.tellus.intensity_provider,
                fragility_provider=self.tellus.fragility_provider
            )

        single_loss_cell = loss.LossCell.from_transition_cell(
            single_transition_cell,
            self.tellus.loss_provider
        )

        return idx, ExposureTransitionAndLossTriple(
            single_updated_exposure_cell,
            single_transition_cell,
            single_loss_cell
        )


# This is a named tuple with an idx, a file name for output
# and one kind of cells (either exposure cells, transition cells
# or loss cells).
IdxOutputFileAndCellsTuple = collections.namedtuple(
    'IdxOutputFileAndCellsTuple', 'idx output_file cells'
)


# This is a named tuple with the exposure cell, the transition
# cell and the loss cell combined.
ExposureTransitionAndLossTriple = collections.namedtuple(
    'ExposureTransitionAndLossTriple',
    'exposure_cell transition_cell, loss_cell'
)


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


def write_result(output_file, cells):
    '''
    Write the updated exposure.
    '''
    if os.path.exists(output_file):
        os.unlink(output_file)
    cells.to_file(output_file, 'GeoJSON')

    # And because we want to reduce the size of the json files
    # as much possible, we will read them and wrote them without
    # any non necessary whitespace (to_file from geopandas
    # introduces some not needed whitespace).
    with open(output_file, 'rt') as read_handle:
        data = json.load(read_handle)
    with open(output_file, 'wt') as write_handle:
        json.dump(data, write_handle)


def write_result_and_convert_to_df(output_file, cells):
    '''
    Same as the write_result but it converts it before
    into a dataframe and returns it too.
    '''
    cells_df = cells.to_dataframe()
    write_result(output_file, cells_df)
    return cells_df


def write_result_and_convert_to_df_tuple(idx_file_cells_tuple):
    '''
    A wrapper for write_result_and_convert_to_df that
    can works with an IdxOutputFileAndCellsTuple as input
    and returns a tuple with the idx of the IdxOutputFileAndCellsTuple
    and the dataframe created out of the cells.

    This is just used for the parallel writing of the output
    files.
    '''
    idx = idx_file_cells_tuple.idx
    output_file = idx_file_cells_tuple.output_file
    cells = idx_file_cells_tuple.cells

    cells_df = write_result_and_convert_to_df(output_file, cells)
    return idx, cells_df
