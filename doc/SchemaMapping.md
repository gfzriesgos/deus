# Schema Mapping

To support different kinds of hazards it is important to
deal with the building classes in other schemas (as the different
hazard experts deal with totally different attributes of buildings).

No schema fits all the needs to support all the hazards, so we need
an approach to map those taxonomies to each other.

## Supported schemas
At the moment we support the SARA and Suppasri 2013 schemas.

## How it works

Currently the approach is splitted into the mapping between taxonomies
(see the `schema_mapping_data_tax` folder) and damage states
(`schema_mapping_data_ds`).

You can see each file as a standalone file.

For taxonomy mappings we have in each file the target and source schemas
as well as a conversion matrix with the source taxonomies as top level
keys, while the target taxonomies are in inner level keys.
The inner level values must sum to 1.

```javascript
{
    "source_schema": "SARA_v1.0",
    "target_schema": "SUPPASRI2013_v2.0", 
    "source_taxonomies": [UNK, ...],
    "target_taxonomies": [RC1, RC2, ...]
    "conv_matrix": {
       "UNK": {
           "RC1": 0.3,
           "RC2": 0.2,
           ...
        },
        ...
    }
}
```

The damage state mappings are similar, but the files also contain
entries for the source taxonomy and the target taxonomy (as the mapping
is specific for these).

*The very most important differnce is that in the conversion matrix
in this files the target_damage states are the toplevel keys,
while the source damage states are the inner level keys.*


## Hard science

It should be said explicitly that there is *no* predefined way on creating those mapping files.
Credits for creating the files included in deus go to
- Max Pittore <pittore@gfz-potsdam.de>
- Simantini Shinde <shinde@gfz-potsdam.de>
- Juan Camilo Gomez <jcgomez@gfz-potsdam.de>

## Don't do it if it is not necessary

Because there is no bidirectional way of doing this kind of mappings, there is always a spread of one
building class to a branch of other ones (same is true for the damage states).
So with each conversion we lose precision of what the original building class and the original damage state
is.

It would also be possible to have all buildings in the highest damage state and to the conversion often enought,
we can get few buildings back to damage state 0.

*So please do the conversion only if necessary.*
