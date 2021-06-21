# deus

[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/gfzriesgos/deus)](https://hub.docker.com/r/gfzriesgos/deus)
[![Build Status](https://travis-ci.com/gfzriesgos/deus.svg?branch=master)](https://travis-ci.com/gfzriesgos/deus)
[![codecov](https://codecov.io/gh/gfzriesgos/deus/branch/master/graph/badge.svg)](https://codecov.io/gh/gfzriesgos/deus)

**D**amage-**E**xposure-**U**pdate-**S**ervice

Command line program for the damage computation in a multi risk scenario
pipeline for earthquakes, tsnuamis, ashfall & lahars.

## Citation
Brinckmann, Nils; Gomez-Zapata, Juan Camilo; Pittore, Massimiliano; Rüster, Matthias (2021): DEUS: Damage-Exposure-Update-Service. V. 1.0. GFZ Data Services. https://doi.org/10.5880/riesgos.2021.011

## What is it?

This is the service to update a given exposure file (as it is the output
of the assetmaster script) and update the building and damage classes
with given fragility functions and intensity values.

## Copyright & License

Copyright (C) 2019-2021
- Nils Brinckmann (GFZ, nils.brinckmann@gfz-potsdam.de)
- Juan Camilo Gomez-Zapata (GFZ, jcgomez@gfz-potsdam.de)
- Massimiliano Pittore (former GFZ, now EURAC Research, massimiliano.pittore@eurac.edu)
- Matthias Rüster (GFZ, matthias.ruester@gfz-potsdam.de)

- Helmholtz Centre Potsdam - GFZ German Research Centre for
  Geosciences (GFZ, https://www.gfz-potsdam.de) 

Licensed under the Apache License, Version 2.0.

You may not use this work except in compliance with the Licence.

You may obtain a copy of the Licence at:
https://www.apache.org/licenses/LICENSE-2.0.txt

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the Licence for the specific language governing
permissions and limitations under the Licence.

## Project

Deus was developed in the scope of the RIESGOS project:
Multi-Risk Analysis and Information System Components for the Andes Region (https://www.riesgos.de/en)


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

There is deus and there is volcanus (a special deus version "volcanus"
that works with shapefiles for intensities - it uses a column LOAD and a unit of kPa -
to allow a special ashfall service in the RIESGOS demonstrator).

The two services only differ in the intensity provider.