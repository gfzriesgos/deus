#!/usr/bin/env python3

# Copyright © 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

"""
Testfile for testing
the intensity provider for rasters.
"""

import rasterio


class RasterIntensityProvider:
    """
    A intensity provider that reads from
    the rasters.
    """

    def __init__(self, data, index, intensity, unit, na_value=0.0):
        self.data = data
        self.index = index
        self.intensity = intensity
        self.unit = unit
        self.na_value = na_value

    def get_nearest(self, lon, lat):
        """
        Samples on the location of lon and lat.
        """
        index = self.index
        try:
            x, y = index(lon, lat)
            value = self.data[0, x, y]
        except IndexError:
            # it is outside of the raster
            value = self.na_value

        intensities = {self.intensity: value}
        units = {self.intensity: self.unit}

        return intensities, units

    @classmethod
    def from_file(cls, filename, intensity, unit, na_value=0.0):
        with rasterio.open(filename) as dataset:
            data = dataset.read()
            # This works as it doesn't need to read any
            # data from the file later.
            def index(x, y):
                return dataset.index(x, y)

        return cls(data, index, intensity, unit, na_value)
