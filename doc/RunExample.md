# Run deus

An example run of deus you can find in the run.sh file:

```shell
#!/bin/bash

python3 deus.py \
    --updated_exposure_output_file updated_exposure_output_file.json \
    --transition_output_file transition_output.json \
    --damage_output_file damage_output.json \
    testinputs/shakemap.xml \
    testinputs/exposure_sara.json \
    'SARA_v1.0' \
    testinputs/fragility_sara.json \
    testinputs/loss_sara.json
```

This script runs deus. It uses:
- The testinputs `shakemap.xml` as intensity input.
  This is an earthquake shakemap with an regular grid.
  You can read about [intensity files](IntensityFile.md) or 
  the [shakemap](EarthQuakeShakemap.md) in particular.
- The testinputs `exposure_sara` file as [exposure model](ExposureModel.md) input.
  It includes only 3 or 4 cells in chile with a bunch of buildings.
- `SARA.0` as input schema for the exposure. This is necessary at the moment
  as there is no schema explicitly named in the exposure model.
  It is used to [map the given taxonomy to another schema](SchemaMapping.md).
- The testinputs `fragility_sara.json` to provide the [fragility functions](FragilityFunctions.md).
- testinputs `loss_sara.json` as provider for the [loss data](LossData.md) for each
  damage state transition.

And it gives specific names for the outputs:
- The first one is the updated exposure model. It follows the same
  format as the input exposure model, but has updated damage states
  for the buildings in the cells. Depending on the fragility model
  it may maps the input before in another schema.
- A json file for the [damage state transitions](DamageStateTransitions.md). It can be used
  to compute the loss later with other tools.
- A json file with the loss computed out of the `loss_sara.json` file.
  This is a kind of default loss computation that may be replaced later.
