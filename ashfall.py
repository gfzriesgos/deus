#!/usr/bin/env python3

"""
Wrapper class to read the ashfall data.
"""

import geopandas

import intensitydatawrapper
import intensityprovider


class Ashfall():

    def __init__(self, gdf, column, name, unit):
        self._gdf = gdf
        self._column = column
        self._name = name
        self._unit = unit

    @classmethod
    def from_file(cls, filename, column, name='LOAD', unit='kPa'):
        """
        Reads the content from a file.
        """
        gdf = geopandas.read_file(filename)
        return cls(
            gdf=gdf,
            column=column,
            name=name,
            unit=unit
        )

    def to_intensity_provider(self):
        """
        Creates the intensity provider.
        """
        intensity_data_wrapper = \
            intensitydatawrapper.GeopandasDataFrameWrapperWithColumnUnit(
                self._gdf,
                column=self._column,
                name=self._name,
                unit=self._unit
            )
        return intensityprovider.IntensityProvider(
            intensity_data_wrapper,
        )
