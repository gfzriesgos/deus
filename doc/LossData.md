# Loss data

The loss data is an input for aggregating the overall loss
of all the transitions.

You can take a look at the file for [SARA](../loss_data/Replacement_cost_SARA_Seismic_v1.json).

The file contains mainly two parts. One is a matrix for coefficients for the damage state
conversions.



So for example, for the SARA we have the following coefficients:

| From | To | Coeff |
|------|----|-------|
|    0 |  1 |  0.02 |
|    0 |  2 |  0.1  |
|    0 |  3 |  0.5  |
|    0 |  4 |  1    |

This way we know that we have 1 * replacement cost for a transition from
0 to 4.

For a transition from 2 to 3 we have a coefficent (0.5 - 0.1) = 0.4.

This way we can compute easily the loss for every transiton that is possible
with the given schema.

The other part in this file is a list of replacementCosts for the taxonomies in the schema.
You should only use this values as fallbacks, as those are constant values and are not country
specific.

If the exposure model contains a column for the `Repl-cost-USD-bdg` those replacement costs are used
and not the ones from the loss files.

The files don't specify a unit. All of our loss computations at the moment are in USD ($).

The loss computation could be extracted from deus later, so that a more sufficient
function can deal with this.