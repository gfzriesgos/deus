# deus

[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/gfzriesgos/deus)](https://hub.docker.com/r/gfzriesgos/deus)
[![Build Status](https://travis-ci.com/gfzriesgos/deus.svg?branch=master)](https://travis-ci.com/gfzriesgos/deus)
[![codecov](https://codecov.io/gh/gfzriesgos/deus/branch/master/graph/badge.svg)](https://codecov.io/gh/gfzriesgos/deus)

*D*amage-*E*xposure-*U*pdate-*S*ervice

## What is it?

This is the service to update a given exposure file (as it is the output
of the assetmaster script) and update the building and damage classes
with given fragility functions and intensity values.

## Documentation

You can look up several documentation pages:

- [Setup and installation](doc/Setup.md)
- [Example run](doc/ExposureModel.md)
- [Shakemaps](doc/EarthQuakeShakemap.md) and [Intensity files](doc/IntensityFile.md)
- [Exposure models](doc/ExposureModel.md)
- [Fragility functions](doc/FragilityFunctions.md)
- [Loss](doc/LossData.md)
- [Schema mappings](doc/SchemaMapping.md)

## Scope of deus

Deus was created in the riesgos project for working in multi risk scenarios.
It should be provided as a web processing service by the GFZ.

## You still have questions

If we don't cover important things in the documentation, please feel free to
create an issue or send a mail at
<nils.brinckmann@gfz-potsdam.de> or <pittore@gfz-potsdam.de>.

## Can I use deus for xyz?

Yes! But you may have to code a bit yourself. The code is written against interfaces
and already provides several implementations for some of them.

Aims for the following development of deus is the support of more and more
hazards with their intensity files, their fragility functions and their schemas.

You can also take a look into the [TODOs](TODO.md).

## Will there only be one deus?

The current version of the code has only one deus and one main function.
However as other hazards don't provide intensity masures in the shakemap
formats it may be necessary to combine different files for one intensity provider.
There is already a class for that (StackedIntenityProvider), but there is no main
function that uses this.

I think it will be possible to work with several deui (damage exposure update implementations),
one for each kind of hazard.
So, something like:

- deus of earth quakes
- deus of tsunamis
- deus of lahars
- deus of ashfalls
- ...
