# Loss data

The loss data is an input for aggregating the overall loss
of all the transitions.

You can take a look into the [example file]{../testinputs/loss_sara.json}.
At the moment all the values for the loss are zero in this file and there
is no unit.

The aim is to provide a way to compute the overall loss and the loss aggregated
for each cell that depends on the single event for which deus was applied for.

The loss computation should be extracted from deus later, so that a more sufficient
function can deal with this.
