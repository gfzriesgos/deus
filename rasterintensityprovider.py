#!/usr/bin/env python3

"""
Testfile for testing
the intensity provider for rasters.
"""

import georasters as gr

class RasterIntensityProvider():
    """
    A intensity provider that reads from
    the rasters.
    """
    def __init__(self, raster, intensity, unit, na_value=0.0):
        self.raster = raster
        self.intensity = intensity
        self.unit = unit
        self.na_value = na_value

    def get_nearest(self, lon, lat):
        """
        Samples on the location of lon and lat.
        """
        try:
            value = self.raster.map_pixel(point_x=lon, point_y=lat)
        except gr.RasterGeoError:
            # it is outside of the raster
            value = na_value

        intensities = {
            self.intensity: value
        }
        units = {
            self.intensity: self.unit
        }

        return intensities, units

    @classmethod
    def from_file(cls, filename, intensity, unit, na_value=0.0):
        raster = gr.from_file(filename)

        return cls(raster, intensity, unit, na_value)

