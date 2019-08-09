#!/usr/bin/env python3

import geopandas as gpd

class ExposureList():

    def __init__(self, gdf):
        self._gdf = gdf

    def __iter__(self):
        for index, row in self._gdf.iterrows():
            yield row

    def to_json(self):
        return self._gdf.to_json()

    @classmethod
    def from_file(cls, file_name):
        gdf = gpd.GeoDataFrame.from_file(file_name)
        return cls(gdf)

    @classmethod
    def from_list(cls, exposure_list):
        gdf = gpd.GeoDataFrame(exposure_list)
        return cls(gdf)
    
