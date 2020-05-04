#TODO-List


This is more a scratch page to collect some ideas on what
to do.
It is not the definitive list of issues to fix.

## Update documentation
The latest changes are not documented in the doc folder, so they should
be updated.

## Check Min- and Max values for fragility functions
In the fragility functions there are min and max intensity values.
If the given intensity is below the min value, than the propability
for a change in the damage state is 0.
Same is true for intensity values greater than the max value.
This way the computation may speed up, because we don't have to compute
the lognorm cdf for at least some transitions (most likely in the
tsunami case, where most of the cells don't have an intensity).

However, we still need to go through all of the cells (at least for the
schema mapping) and - to be honest - also through all of the taxonomies
in the cells, because this values are taxonomy dependent and they
can rely on different intensity measurements (PGA, SA(1.0), SA(0.3), ...).

## grd file support

It should be relativly easy to support grd files as inputs for intensity
measurements.

## Refactor loss computation

Currently the loss values for each transition are stored in the `loss_data`
folder. 

With this strategy we can't support country / region specific replacement
costs.

However, for the sara schema all the loss values follow some rules:

| From |  To |        Factor |
|------|-----|---------------|
|    0 |   1 |          0.02 |
|    0 |   2 |           0.1 |
|    0 |   3 |           0.5 |
|    0 |   4 |             1 |
|    1 |   2 | (0.1 - 0.02 ) |
|  ... | ... |           ... |

The factor is different for each taxonomy.

The very first step would be to replace the existing loss files with smaller files
that contain just this factor information.

And the second step is to neglect the taxonomy specific factor and use replacement costs
from the exposure model.

### Replacement costs on the exposure model

First they are additional columns in the inner expo dict in the geojson (so we
have one row for each cell, each taxonomy and each damage state).

At the beginning (in damage state 0) they are equivalent to our loss values
from 0 to the highest damage state.

So lets have an example of a building class with CR-LDUAL-DUC-H4-7 (because it is
the very first element in the current loss value file). It starts with a damage state of
0 and a replacement-cost-value of 1080000.0.

We then need to go into a higher damage state, let's say 1.
We now know that our loss value will be like 0.02 of the replacement costs (because
we know that it is a transition from 0 to 1). We can add that to our over all loss.

Because of this scaling we are not even interested in what taxonomy it really is.

We can use the very same idea to compute the loss for later transitions (say from
3 to 4), as we now that we have to take 0.5 times the replacement-costs from the
exposure model.

But what is about the schema mapping?

In the schema mapping we split the building from one group (taxonomy & damage state tuple)
to several other groups. Using this relative numbers we can also split the replacement
costs (so that we have 3 groups out of one original group and the sum of our replacement
costs stay the same; but only if those numbers are total numbers for all the buildings
in the group). 

## Adding overall loss

At the moment the handling of the different columns is a bit inconsistent.
We update the expo column (containing data from older runs), but we write new 
loss columns all the time (containing no data from older runs).

So it would be meaningful starting to aggregate the overall loss over mulitiple
runs.

