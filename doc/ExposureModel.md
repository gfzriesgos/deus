# Exposure Model

The exposure model is a list of geo cells with the number of buildings
in various building classes.

Think it as the following:

|        name |  expo | gid |          geometry |
|-------------|-------|-----|-------------------|
| Casa Blanca | {...} | CH1 | MULTIPOLYGON(...) |
|     Quilpue | {...} | CH2 | MULTIPOLYGON(...) |
|         ... |  ...  | ... |              ...  |


The inner expo dataset is itself an table like structure:

|           id | Region | Taxonomy | ... | Buildings | ... | Damage |
|--------------|--------|----------|-----|-----------|-----|--------|
| AREA # 13301 | Colina |        W | ... |     100.0 | ... |     D0 |
| AREA # 13301 | Colina |        W | ... |      50.0 | ... |     D1 |
|          ... |    ... |      ... | ... |       ... | ... |    ... |
| AREA # 13301 | Colina |        S | ... |     200.0 | ... |     D0 |
| AREA # 13301 | Colina |        S | ... |      20.0 | ... |     D1 |
|          ... |    ... |      ... | ... |       ... | ... |    ... |

The most important fields for deus are taxonomy, damage and buildings (number of buildings in
this cell, for this taxonomy and damage state).

Other included fields are:
- Dwellings
- `Repl_cost_USD/bdg`
- Population
- name

Some of the fields are all the same for the spatial cell, some differ
per taxonomy and damage state combination.

CAUTION: Currently is there no proper handling of the replacement costs
per buildings, as this is schema, taxonomy and damage state dependent.
We can't use them here because we may map to a different schema and
increase the damage states.

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

## Transition output

We also write a transition file out with all the increases of damage states in the deus run.

The model follows the one of the exposure model, but instead of the expo element we have a
transitions element with a tabular structure.

| taxonomy | from damage state | to damage state | n buildings |
|----------|-------------------|-----------------|-------------|
|        W |                 0 |               1 |       100.0 |
|        W |                 0 |               2 |        50.0 |
|        W |                 0 |               3 |        20.0 |
|      ... |               ... |             ... |         ... |
|        W |                 1 |               2 |        40.0 |
|      ... |               ... |             ... |         ... |
|        S |                 0 |               1 |       200.0 |
|      ... |               ... |             ... |         ... |

As this table is specific for each spatial cell, we can also compute the overall loss
on cell level later.
