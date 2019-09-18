#!/usr/bin/env python3

'''
This is a module to provide wrappers
for different possible apis to deal
with raster data.
'''


class RasterWrapperRio():
    '''
    This is a wrapper using the rasterio
    api to get on the data.
    '''

    def __init__(self, raster_reader):
        self._raster_reader = raster_reader
        self._data = raster_reader.read()

    def is_loaction_in_bbox(self, lon, lat):
        '''
        Tests if a location is in the bounding box of the
        raster.
        '''
        bbox = self._raster_reader.bounds
        if lon < bbox.left:
            return False
        if lon > bbox.right:
            return False
        if lat < bbox.bottom:
            return False
        if lat > bbox.top:
            return False

        return True

    def get_sample(self, lon, lat):
        '''
        Returns the value at the given location.
        Please note: This function does not test if
        the location is in the bounding box of the data.
        Please check that before you query the values!.
        '''
        idx = self._raster_reader.index(lon, lat)
        # at the moment it only supports one band
        return self._data[0, idx[0], idx[1]]


class RasterWrapper():
    '''
    This is a wrapper using the georasters
    api to get on the data.
    '''
    def __init__(self, raster):
        self._raster = raster

    def is_loaction_in_bbox(self, lon, lat):
        '''
        Tests if a location is in the bounding box of the
        raster.
        '''
        if lon < self._raster.xmin:
            return False
        if lon > self._raster.xmax:
            return False
        if lat < self._raster.ymin:
            return False
        if lat > self._raster.ymax:
            return False
        idx = self._raster.map_pixel_location(lon, lat)
        if any(idx < 0):
            return False
        return True

    def get_sample(self, lon, lat):
        '''
        Returns the value at the given location.
        Please note: This function does not test if
        the location is in the bounding box of the data.
        Please check that before you query the values!.
        '''
        return self._raster.map_pixel(lon, lat)
