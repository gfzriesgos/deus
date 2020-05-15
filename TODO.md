#TODO-List

This is more a scratch page to collect some ideas on what
to do.
It is not the definitive list of issues to fix.

## Check if all of the cells needs to be updated
As our intensities are only applied locally (and not in the full
spatial coverage of our exposure model), we can skip the damage computation
for a lot of cells (because lognorm cdf computation is expensive).

This is true especially for tsunami intensities as those only effects
the coast line (and barely any cell behind).

However, we have to keep in mind that our fragility functions care about
different units for the intensities, depending on the taxonomy.

## grd file support

It should be relativly easy to support grd files as inputs for intensity
measurements.

## Adding overall loss

At the moment the handling of the different columns is a bit inconsistent.
We update the expo column (containing data from older runs), but we write new 
loss columns all the time (containing no data from older runs).

So it would be meaningful starting to aggregate the overall loss over mulitiple
runs.

