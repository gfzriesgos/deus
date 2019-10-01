# How it works

## Input & Output
Deus consists of 4 kinds of input datasets:
- [intensity file](IntensityFile.md)
- [an existing exposure model](ExposureModel.md)
- [fragility functions](FragilityFunctions.md)
- [loss data](LossData.md)

It outputs the updated exposure model, a [list with all the
damage state transitions](DamageStateTransitions.md)
and a aggregated loss out of this
conversions.

## Processing

The pipeline of deus is the following:

1. Iterate over all the cells in the exposure model
2. [Map the taxonomy](SchemaMapping.md) of the cell from the input schema to the
   schema of the fragility functions
3. Get the intensity on the centroid of the cell
4. For each building class and damage state in the taxonomy
   it computes the probability
   of a building to switch into a higher damage state
5. It computes how many buildings switch into those higher damage states
   and keeps track of the transitions per cell.
6. It computes the overall loss of all the transitions in the cell.
7. Once it is done with iterating over all the cells deus
   writes the collected updated exposure cells, the transitions
   and the computed loss into files.

## Multiple events

Deus is implemented in a way that you can apply several events, so that you can update
the exposure model and the damage states of the buildings with each earth quake / tsunami / ... .
Just make sure that you insert the updated exposure model as input exposure model to the next
deus run.

## Supported hazards

At the moment deus supports earth quake events via [shakemaps](EarthQuakeShakemap.md) and
tsunamis via [tsunami shakemaps](TsunamiShakemap.md).

You can include other hazards by implementing access to the [intensity data formats](IntensityFile.md),
the custom [fragility functions](FragilityFunctions.md) and - if you want to apply it to exposure models
of other hazards - [schema mapping files]{SchemaMapping.md}.

## Supported crs

Deus does not care about the crs as long as the intensity and the exposure are in the same coordinate
reference system. You can use geopandas to transform vector data on the fly. For raster data the georasters
package does not support reprojections at the moment, so please make sure, that you use the same crs for
exposure and intensity data before starting deus.
