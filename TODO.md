#TODO-List


This is more a scratch page to collect some ideas on what
to do.
It is not the definitive list of issues to fix.


# Change the schema mapping files

```
{"source_schema": "SARA_v1.0",
 "source_taxonomy": "CR_...",
 "target_schema": "SUPPASRI2013_v2.0",
 "target_taxonomy": "W",
 "conv_matrix": { ...}}
```

(Will be done by Sim).

## Add files to read the building class mappings between schemas
We want to provide additional files for other schemas.
## Add name of input exposure taxonomy to exposure file (+ and to updated)
At best the very same name as the fragility files uses as ids.
## Check for updates in Assetmaster and Modelprop
Should be done from time to time to ensure that this service can still
read the fragility data *AND* uses the same output format as the
exposure data that is given as input.
## Clear imt field in fragility files
At the moment I use them to read the correct value out of the shakemap,
so that it is 'pga' for earth quakes.
The tsunami shakemaps have the intensity as mwh - maximum wave height,
so that should be in the imt field for the fragility files for supparsi.

If it can't be used for this - so that it has another meaning and I'm
just wrong with my idea to use it to read the intensity value -
the code must be changed.
## Add unit handling for loss computation
At the moment this are just numbers (all zeros), but there should be
meaningful values *and units*
## Clear loss data file
Either use one loss data file that the user provides by herself or
integrate several for all the supported schemas and just integrate
them in the repository itself (as the files for the conversion between
damage states and building classes).
## Repojection support for raster files
Intensity data in a geopandas dataframe can be used reprojected on the fly to
a different coordinage system. The georasters module has actually no way to this,
so a switch to the rasterio package (with wrap support) should be done.
