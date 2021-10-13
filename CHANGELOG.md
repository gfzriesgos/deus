# 3021-10-13:

- added support for the Medina 2019 scheme

# 2020-05-13:

- removed `im_min` and `im_max` handling as those have a bad performance characteristic
  and are too broad to be useful (they are specific for the taxonomy and *not* for
  damage states)
- Some changes to improve performance in the exposure handling

# 2020-05-12:

- added usage of `im_min` and `im_max` values for computing probabilities
  out of the fragility functions (i < `im_min` --> 0; i > `im_max` --> 1)

# 2020-05-11:

- Mapping and exposure update now handles the population and the replacement costs per building
- Loss computation now uses the replacement costs per building (there is a fallback if there are non, so we reuse the data from the loss files that we already have)
- updated the documentation
- removed unused classes and their test cases

# 2020-02-03:

- Added a new output parameter that contains all the outputs of the older three
  (updated exposure model, transitions & damage).

# 2019-11-20:

- Updated replacement costs

# 2019-11-19:

- Switched the intensity input for volcanus wps to geojson
  to fix a problem with giving both shapefiles and geojson

# 2019-11-14:

- Added another sub program to work with ashfall data

# 2019-11-13:

- Added new replacement cost files for the riesgos ecuador show case

# 2019-11-11:

- Added the schema mapping files for the SARA W-WWD-H1-2 taxonomy

# 2019-11-08:

- Replaced the replacement costs for sara with the country specific
  one for peru

# 2019-11-07:

- Performance improvements for Schema Mapping and merges for
  taxonomy+damagestate combinations and transitions

# 2019-11-04:

- Added support for strings in shakemap grid data
- Added support for intensity aliases to get their value
  from columns with different names (say one uses MHW, another
  INUN\_MEAN\_POLY, but both should be used as ID - for inundation)

# 2019-10-28:

- Updated the damage state schema mapping files

# 2019-10-25:

- Fixed the schema mapping

# 2019-10-23:

- Added a intensity provider that directly work with raster files

# 2019-10-10:

- Integrated the loss data files to be part of deus, so
  the user does not have to give to the calls for deus anymore
- Added aliases for intensity measurements

# 2019-09-18

- Added the changelog
- Rewrote documentation
- Added RasterIntensityProvider
