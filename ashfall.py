#!/usr/bin/env python3

# Damage-Exposure-Update-Service
# 
# Command line program for the damage computation in a multi risk scenario
# pipeline for earthquakes, tsnuamis, ashfall & lahars.
# Developed within the RIESGOS project.
#
# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
#
# Parts of this program were developed within the context of the
# following publicly funded projects or measures:
# -  RIESGOS: Multi-Risk Analysis and Information System 
#    Components for the Andes Region (https://www.riesgos.de/en)

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
