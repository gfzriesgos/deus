# Intensity file

An intensity file provides the data - values and units - of the intenity
that we want to read on the locations of the exposure model.

## Supported intensity file formats
At the moment the following formats are supported by the default deus:
- earth quake shakemaps with regular grids
- tsunami shakemaps with irregular grids

## Intensity provider interface
To support other formats in the future we introduced an interface for
getting the intensity values.

It follows to implement the `get_nearest` method, so that you can give
it the lon and lat values.

All implementations should give back two dicts with the intensity values
and the units of all the fields that are included in the file.

```
intensities, units = intensity_provider.get_nearest(lon=lon, lat=lat)
```

In case of the earth quake shakemap implementation the keys in the 
dicts are pga and stdpga (for the standard derivation).

## Raster support

You can use classes from the rasterwrapper module togehter with the
RasterIntensityProvider implementation from the intensityprovider module,
to access raster cells.
