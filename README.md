[![Build Status](https://travis-ci.com/gfzriesgos/deus.svg?branch=master)](https://travis-ci.com/gfzriesgos/deus)

# deus

*D*amage-*E*xposure-*U*pdate-*S*ervice


## What is it?

This is the service to update a given exposure file (as it is the output
of the assetmaster script) and update the building and damage classes
with given fragility functions and intensity values.


## Inputs

### Intensity Map

The intensity map should be given in a format of a USGS shakemap.
It contains a regular grid for a given area and the intensity values
(the PGA) for each cell value. It can also contain heights in case of
a tsunami simulation.

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

### Fragility Functions

The fragility functions define the probability of a specific damage
state for a building class on a given intensity (so they are specific
to the building class and the damage class).


## Output

The output is the updated exposure model.
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
damages of several earthquakes / tsunamis / ...


## Supported hazards

This service is meant to not just to support earthquakes, but also to
support tsunamis or other hazards as long as they provide a shakemap
object as input for the intensities and a predefined way to convert
the building classes with damage states from one schema to another (if
the hazard fragility functions use a different schema).
