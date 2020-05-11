#TODO-List


This is more a scratch page to collect some ideas on what
to do.
It is not the definitive list of issues to fix.

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

## Adding overall loss

At the moment the handling of the different columns is a bit inconsistent.
We update the expo column (containing data from older runs), but we write new 
loss columns all the time (containing no data from older runs).

So it would be meaningful starting to aggregate the overall loss over mulitiple
runs.

