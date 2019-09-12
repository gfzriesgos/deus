#TODO-List

## Add files to read the building class mappings between schemas
(We want to provide additional files for other schemas.)
## Add name of input exposure taxonomy to exposure file (+ and to updated)
(At best the very same name as the fragility files uses as ids).
## Think about having columns for damage state
(So that there is no `_DXX` at the end of the taxonomy).
## Check for updates in Assetmaster and Modelprop
(Should be done from time to time to ensure that this service can still
read the fragility data *AND* uses the same output format as the
exposure data that is given as input).
## Clear imt field in fragility files
(At the moment I use them to read the correct value out of the shakemap,
so that it is 'pga' for earth quakes.
The tsunami shakemaps have the intensity as mwh - maximum wave height,
so that should be in the imt field for the fragility files for supparsi.)

(If it can't be used for this - so that it has another meaning and I'm
just wrong with my idea to use it to read the intensity value -
the code must be changed).
## Add unit handling for loss computation
(At the moment this are just numbers (all zeros), but there should be
meaningful values *and units*)
## Update readme
- purpose of deus
- installation
- example files
- usage
## Clear loss data file
Either use one loss data file that the user provides by herself or
integrate several for all the supported schemas and just integrate
them in the repository itself (as the files for the conversion between
damage states and building classes).
## Raster handling
The current version of reading the raster cells is really slow.
We should make sure that we can run much faster (without the conversion
to a geopandas dataframe).
