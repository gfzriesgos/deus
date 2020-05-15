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

| Taxonomy | Buildings | Damage | Population | Repl-cost-USD-bdg |
|----------|-----------|--------|------------| ------------------|
|        W |     100.0 |     D0 |        100 |             32003 |
|        W |      50.0 |     D1 |        ... |               ... |
|      ... |       ... |    ... |        ... |               ... |
|        S |     200.0 |     D0 |        ... |               ... |
|        S |      20.0 |     D1 |        ... |               ... |
|      ... |       ... |    ... |        ... |               ... |

The most important fields for deus are taxonomy, damage and buildings (number of buildings in
this cell, for this taxonomy and damage state).
There are two other fields:

- Population: The population in the exposure cell for the taxonomy and the damage state.
- `Repl-cost-USD-bdg`: The replacement costs per building. This is always a value
  for damage state 0.


## Schemas
The building class belongs to a taxonomy of a given schema.
Currently only some schemas are supported.
You can take a look in the [documentation of the mapping](SchemaMapping.md).

## Geographical information
At the moment we are only interestend in the centroid of the cell to get the intensity as this
is the point for which we aggregate all the building data.

## Updated exposure model
The updated exposure model is identical to the input exposure model after two processing steps:
- The building classes and damage states are mapped to another schema if the fragility functions
  and the intensity file makes it necessary
- The buildings and population fields are transfered from one damage state to a higher one according to the intensity
  and the fragility functions.

## Transition output

We also write a transition file out with all the increases of damage states in the deus run.

The model follows the one of the exposure model, but instead of the expo element we have a
transitions element with a tabular structure.

You can take a look [here](DamageStateTransitions.md)