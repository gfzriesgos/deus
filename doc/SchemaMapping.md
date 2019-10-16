# Schema Mapping

To support different kinds of hazards it is important to
deal with the building classes in other schemas (as the different
hazard experts deal with totally different attributes of buildings).

No schema fits all the needs to support all the hazards, so we need
an approach to map those taxonomies to each other.

## Supported schemas
At the moment we support the SARA and Suppasri 2013 schemas.

## How it works
The mapping is done via the files in the `schema_mapping_data` folder.
It follows a format to have a json file for each building class in a schema to
another building class in the target schema.

## Mapping file by example
One file follows the following format:

```javascript
{
    "source_schema": "SARA",
    "source_taxonomy": "MUR_H1", 
    "target_schema": "SUPPASRI_2013", 
    "target_taxonomy": "W1", 
    "source_damage_states": [0, 1, 2, 3, 4], 
    "target_damage_states": [0, 1, 2, 3, 4, 5, 6], 
    "conv_matrix": "{\"0\":{\"0\":0.0000000002,\"1\":0.0,\"2\":0.0,\"3\":2.147685954e-17,...
```

For each source building class there are several target files.

The most important part is the conversion matrix, which contains on which part one building of the
source and with a given damage state is mapped to other damage states in target.

So the format is:

```
"damage_state_in_source1": {
    "damage_state_in_target1": p_1_1,
    "damage_state_in_target2": p_1_2,
    ...
},
"damage_state_in_source2": {
    "damage_state_in_target1": p_2_1,
    "damage_state_in_target2": p_2_2,
    ...
},
...
```

We can add other supported schema mappings by just inserting new files in the `schema_mapping_data`
folder.`

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
