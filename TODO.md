#TODO-List

## Add files to read the building class mappings between schemas
(Should follow the same structure as the mapping files for the damage states).
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

## Keep track of the transitions
(How many buildings go from one damage state to another).
(Should be the transitions of the data *after* the mapping to another
schema). (It is very important that the base damage state is,
so that we can list them (RC_D0 -> D1 : 20,
RC_D1 -> RC_D2 : -5,
RC_D2 -> RC_D3: 30, ...)

--> Switch to file based output for all the outputs.

And the mapping (conversion) must be applied before using the
fragility functions (so that we have the aggregated mapped taxonomy as
the base for keeping track of the transitions).

Still computing on the geocell level, so that we can take care about
the spatial pattern)

## Compute Loss
There should be also a service for computing the damage (it will get
the geocells and the transitions (or a list of transitions for
different events). This will compute the loss. (And it will be very
important to care about the intermediate transitions).

Maybe it can be integrated into deus, but there will be definitivly
another service for this.
