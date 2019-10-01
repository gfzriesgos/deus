# Exposure Model

The exposure model is a list of geo cells with the number of buildings
in various building classes.

Think it as the following:

|        Area |    Building class | Damage state | Number of buildings |
|-------------|-------------------|--------------|---------------------|
| Casa Blanca | CR_LFINF_H1_3_DUC |            0 |                 100 |
| Casa Blanca |   CR_LFM_H1_3_DNO |            0 |                  80 |
|         ... |               ... |          ... |                 ... |
|     Quilpue |   CR_LFM_H1_3_DNO |            0 |                 120 |
|         ... |               ... |          ... |                 ... |


## Schemas
The building class belongs to a taxonomy of a given schema.
Currently only some schemas are supported.
You can take a look in the [documentation of the mapping](SchemaMapping.md).


## Encoding of the damage states
As the overall structure of the exposure model is given as a geojson file,
we need to encode the damage state information with the building class.

The used approach here is: `builing class name -> underscore -> damage state value at the end`
so for example `CR_LFM_H1_3_DNO_D2` for the building class `CR_LFM_H1_3_DNO` in damage state
2.

If the data lacks any information about the damage states - for a clean exposure model for example -
all damage states are zero.

## Geographical information
At the moment we are only interestend in the centroid of the cell to get the intensity as this
is the point for which we aggregate all the building data.

## Updated exposure model
The updated exposure model is identical to the input exposure model after two processing steps:
- The building classes and damage states are mapped to another schema if the fragility functions
  and the intensity file makes it necessary
- The buildings are transfered from one damage state to a higher one according to the intensity
  and the fragility functions.
