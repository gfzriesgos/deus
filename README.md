[![Build Status](https://travis-ci.com/gfzriesgos/deus.svg?branch=master)](https://travis-ci.com/gfzriesgos/deus)

# deus

*D*amage-*E*xposure-*U*pdate-*S*ervice


## What is it?

This is the service to update a given exposure file (as it is the output
of the assetmaster script) and update the building and damage classes
with given fragility functions and intensity values.

## How does it works?

Deus gets an existing exposure model, fragility functions and an intensity
map.

The first step is to map the existing exposure model to the schema
of the fraglity functions. You can see supported schemas in the section for
schema mappings.

The next part is to evaluate the intensity map on the centroid points of the
spatial cells and to use this values in the fragility functions.

These functions provide a probability for a building to switch to another
damage state.

With that value we know how many buildings in our cell are getting more damaged.

This transitions are collected and together with loss data we compute
the overall loss for the event regarding to damage state changes for the
buildings in our expsure model.

With the output of the updated exposure model it is possible to run deus
multiple times for multiple events or other hazards as well.


## Inputs

### Intensity Map

The intensity map should be given in a format of a USGS shakemap.
It contains a regular grid for a given area and the intensity values
(the PGA) for each cell value. It can also contain heights in case of
a tsunami simulation.

Since an extension for the tsunami support we also support tsunami shakemaps.

An example shakemap looks like this:

```xml
`<?xml version='1.0' encoding='UTF-8'?>
<ns1:shakemap_grid 
    xmlns:ns1="http://earthquake.usgs.gov/eqcenter/shakemap" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns="http://earthquake.usgs.gov/eqcenter/shakemap" 
    code_version="shakyground 0.1" 
    event_id="quakeml:quakeledger/466776" 
    map_status="RELEASED" 
    process_timestamp="2019-08-08T12:31:27.890823Z" 
    shakemap_event_type="stochastic" 
    shakemap_id="quakeml:quakeledger/466776" 
    shakemap_originator="GFZ" 
    shakemap_version="1" 
    xsi:schemaLocation="http://earthquake.usgs.gov 
        http://earthquake.usgs.gov/eqcenter/shakemap/xml/schemas/shakemap.xsd"
>
    <event 
        depth="97.99416" 
        event_description="" 
        event_id="quakeml:quakeledger/466776" 
        event_network="nan" 
        event_timestamp="90175-01-01T00:00:00.000000Z" 
        lat="-33.60348" 
        lon="-70.43199" 
        magnitude="7.4"
    />
        <grid_specification 
            lat_max="-32.65" 
            lat_min="-34.5583333333" 
            lon_max="-69.6416666667" 
            lon_min="-71.225" 
            nlat="230" 
            nlon="191" 
            nominal_lat_spacing="0.008333" 
            nominal_lon_spacing="0.008333" 
            regular_grid="1"
        />
        <event_specific_uncertainty name="pga" numsta="" value="0.0"/>
        <event_specific_uncertainty name="pgv" numsta="" value="0.0"/>
        <event_specific_uncertainty name="mi" numsta="" value="0.0"/>
        <event_specific_uncertainty name="psa03" numsta="" value="0.0"/>
        <event_specific_uncertainty name="psa10" numsta="" value="0.0"/>
        <event_specific_uncertainty name="psa30" numsta="" value="0.0"/>
        <grid_field index="1" name="LON" units="dd"/>
        <grid_field index="2" name="LAT" units="dd"/>
        <grid_field index="3" name="PGA" units="g"/>
        <grid_field index="4" name="STDPGA" units="g"/>
        <grid_data>
-71.21666666670001 -32.65 0.056063764 0.7362585
-71.2083333333 -32.65 0.057824578 0.7362585
-71.2 -32.65 0.06327598 0.7362585
-71.1916666667 -32.65 0.059195064 0.7362585
-71.1833333333 -32.65 0.053293496 0.7362585
-71.175 -32.65 0.054376625 0.7362585
-71.1666666667 -32.65 0.060831208 0.7362585
...
```

### Exposure Model

The exposure model can be treated like a table.
It lists spatial cells with the different building classes and the
number of buildings in each class.

| Class | n   |
|-------|-----|
| URM   | 100 |
| RC    | 50  |
| W     | 179 |
| ...   | ... |


For the initial input all the building classes have no damage state at all.
The main part of deus work is to update the damage states of the buildings in the cells.


### Fragility Functions

The fragility functions define the probability of a specific damage
state for a building class on a given intensity (so they are specific
to the building class and the damage class).

DEUS supports mappings from damage state 0 (so no damage) to another damage states,
as well as intermediate transitions.

An example file - without explicit fragility functions for transitions between
damage states - would look like this:

```
`{
    "meta": {
        "id": "SARA.0",
        "assetCategory": "buildings",
        "lossCategory": "structural",
        "taxonomy_source": "GEM",
        "damage_states": "SARA",
        "format": "continuous",
        "shape": "logncdf",
        "description": "GEM-SARA Model, project RIESGOS",
        "taxonomies": [
            "MUR_H1",
            "ER_ETR_H1_2",
            ...
        ],
        "limit_states": [
            "D1",
            "D2",
            "D3",
            "D4"
        ]
    },
    "data": [
      {
            "taxonomy": "MUR_H1",
            "D1_mean": -1.418,
            "D1_stddev": 0.31,
            "D2_mean": -0.709,
            "D2_stddev": 0.328,
            "D3_mean": -0.496,
            "D3_stddev": 0.322,
            "D4_mean": -0.231,
            "D4_stddev": 0.317,
			"id":"unique_id",
			"imt":"pga",
			"imu":"g",
			"im_min":0.0,
			"im_max":1.0
        },
        {
            "taxonomy": "ER_ETR_H1_2",
            "D1_mean": -1.418,
            "D1_stddev": 0.31,
            "D2_mean": -0.709,
            "D2_stddev": 0.328,
            "D3_mean": -0.496,
            "D3_stddev": 0.322,
            "D4_mean": -0.231,
            "D4_stddev": 0.317,
			"id":"unique_id",
			"imt":"pga",
			"imu":"g",
			"im_min":0.0,
			"im_max":1.0
        },
        ...
```

To insert fragility functions for intermediate damage states, follow the naming schema
as 
`D_i_j_mean`
with i as the source damage state and j as the target damage state.

At the moment only lognorm cdf shapes for the fragility functions are supported.

Please note:
The imt values in the fragility functions are the values that must be provided by the
intensity maps and the imu values must match their units.

### Loss data

The fourth input is data for computing the losses out of the transitions.
Here is ongoing work necessary to provide meaningful values and units for loss.

## Output

### Updated exposure model

The spatial cells remain but the number of buildings are now splitted
into damage states:

| Class with damage state | n   |
|-------------------------|-----|
| URM D0                  | 60  |
| URM D1                  | 25  |
| URM D2                  | 15  |
| RC D0                   | 30  |
| RC D1                   | 15  |
| RC D2                   | 5   |
| ...                     | ... |


The output is also meant to be input for another loop through this
update process. This is important to support the option to compute the
damages of several earthquakes / tsunamis / eetc.


### Transition output

Another output is a table with all of the damage state transitions.
This is seperate for each spatial cell and each building class.

### Loss output

Given the loss for each transition we also compute the loss.
This is done in each geocell to allow analyzing spatial differences.

## Supported hazards

This service is meant to not just to support earthquakes, but also to
support tsunamis or other hazards as long as they provide a shakemap
object as input for the intensities and a predefined way to convert
the building classes with damage states from one schema to another (if
the hazard fragility functions use a different schema).

Supporting additional hazards is a work on supporting the associated schemas,
the fragility functions for these hazards and on reading the intensity files
in the common data formats.

## Supported schemas

At the moment we support the SARA and Suppasri 2013 schemas.
The mapping is done via the files in the `schema_mapping_data` folder.
It follows a format to have a json file for each building class in a schema to
another building class in the target schema.

One file follows the following format:

```javascript
{
    "source_name": "SARA_MUR_H1", 
    "target_name": "SUPPARSI_2013_W1", 
    "source_damage_states": [0, 1, 2, 3, 4], 
    "target_damage_states": [0, 1, 2, 3, 4, 5, 6], 
    "conv_matrix": "{\"0\":{\"0\":0.0000000002,\"1\":0.0,\"2\":0.0,\"3\":2.147685954e-17,...
```

The source name is the source schema together with the building class.
Same is true for the target name, except that the target schema and building classes is used.
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
}
```

We can add other supported schema mappings by just inserting new files in the `schema_mapping_data`
folder.`
