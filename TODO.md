#TODO-List


This is more a scratch page to collect some ideas on what
to do.
It is not the definitive list of issues to fix.

## Update documentation
The latest changes are not documented in the doc folder, so they should
be updated.

## Check Min- and Max values for fragility functions
In the fragility functions there are min and max intensity values.
If the given intensity is below the min value, than the propability
for a change in the damage state is 0.
Same is true for intensity values greater than the max value.
This way the computation may speed up, because we don't have to compute
the lognorm cdf for at least some transitions (most likely in the
tsunami case, where most of the cells don't have an intensity).

However, we still need to go through all of the cells (at least for the
schema mapping) and - to be honest - also through all of the taxonomies
in the cells, because this values are taxonomy dependent and they
can rely on different intensity measurements (PGA, SA(1.0), SA(0.3), ...).

## Add support for the ashfall data

For the ecuador showcase in RIESGOS we have to support the ashfall data
(pressure in kPa).

I think they will be delivered as shapefiles in wgs84.
However they contain several measurements (different months) 
and we must have a
clear and meaningful way to select/combine them.
Maybe we also have to extend the way the fragility functions in deus
work.

## Repojection support for raster files
Intensity data in a geopandas dataframe can be used reprojected on the fly to
a different coordinage system. The georasters module has actually no way to this,
so a switch to the rasterio package (with wrap support) should be done.
