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

import gpdexposure
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
            old_exposure,
            exposure_schema,
            loss_provider,
            args_with_output_paths):
        self.intensity_provider = intensity_provider
        self.fragility_provider = fragility_provider
        self.old_exposure = old_exposure
        self.exposure_schema = exposure_schema
        self.loss_provider = loss_provider
        self.args_with_output_paths = args_with_output_paths

    def run(self):
        """
        All the work is done here.
        """
        current_dir = os.path.dirname(__file__)
        schema_mapper = create_schema_mapper(current_dir)
        result_exposure = gpdexposure.update_exposure_transitions_and_losses(
            self.old_exposure, self.exposure_schema, schema_mapper,
            self.intensity_provider, self.fragility_provider,
            self.loss_provider
        )

        jobs_for_writing = [
            FilterColumnsAndWriteResult(
                result_exposure,
                self.args_with_output_paths.updated_exposure_output_file,
                ['gid', 'geometry', 'expo']),
            FilterColumnsAndWriteResult(
                result_exposure,
                self.args_with_output_paths.transition_output_file,
                ['gid', 'geometry', 'transitions']),
            FilterColumnsAndWriteResult(
                result_exposure,
                self.args_with_output_paths.loss_output_file,
                ['gid', 'geometry', 'loss_value', 'loss_unit']),
            FilterColumnsAndWriteResult(
                result_exposure,
                self.args_with_output_paths.merged_output_file
            ),
        ]

        with multiprocessing.Pool() as pool:
            pool.map(FilterColumnsAndWriteResult.run, jobs_for_writing)


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


class FilterColumnsAndWriteResult:
    def __init__(self, raw_df, path, columns=None):
        self.raw_df = raw_df
        self.path = path
        self.columns = columns

    def run(self):
        if self.columns:
            df = self.raw_df[self.columns]
        else:
            df = self.raw_df
        write_result(self.path, df)
