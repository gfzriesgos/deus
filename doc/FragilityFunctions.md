# Fragility Functions

The fragility functions specify the probability of a building class of a certain damage
state to get damaged even more and switch into a higher damage state.

## Example file

You can take a look into an [example file](../testinputs/fragility_sara.json).

## The most important fields

```javascript
{
    "meta": {
        "id": "SARA.0",
        "assetCategory": "buildings",
        "lossCategory": "structural",
        "taxonomy_source": "GEM",
        "damage_states": "SARA",
        "format": "continuous",
        "shape": "logncdf",
        "description": "GEM-SARA Model, project RIESGOS",
        "taxonomies": [
            "MUR_H1",
            "ER_ETR_H1_2",
            "MUR_H1_3",
            "MUR_ADO_H1_2",
            "MUR_STRUB_H1_2",
            "MR_H1_3_DUC",
            "MCF_H1_3_DUC",
            "MCF_H1_3_DNO",
            "MR_H1_3_DNO",
            "CR_LFM_H1_3_DUC",
            "CR_LFLS_H1_3_DUC",
            "CR_LFM_H4_7_DUC",
            "CR_LFLS_H4_7_DUC",
            "CR_LDUAL_H4_7_DUC",
            "CR_LFLS_H1_3_DNO",
            "CR_LFM_H1_3_DNO",
            "CR_LFM_H4_7_DNO",
            "CR_LFM_H1_3_DNO_SOS",
            "CR_LFM_H4_7_DNO_SOS",
            "CR_LFINF_H1_3_DUC",
            "CR_LWAL_H1_3_DUC",
            "CR_PC_LWAL_H1_3",
            "CR_LFINF_H_4_7_DUC",
            "CR_LWAL_H4_7_DUC",
            "CR_LFINF_H1_3_DNO",
            "CR_LWAL_H1_3_DNO",
            "CR_LWAL_H4_7_DNO",
            "CR_LDUAL_H8_19_DUC",
            "CR_LWAL_H8_19_DUC",
            "W_WLI_H1_3",
            "W_WHE_H1_3",
            "W_WS_H1_2",
            "W_WBB_H1",
            "UNK"
        ],
        
        "limit_states": [
            "D1",
            "D2",
            "D3",
            "D4"
        ]
     
    },
    "data": [
      {
            "taxonomy": "MUR_H1",
            "D1_mean": -1.418,
            "D1_stddev": 0.31,
            "D2_mean": -0.709,
            "D2_stddev": 0.328,
            "D3_mean": -0.496,
            "D3_stddev": 0.322,
            "D4_mean": -0.231,
            "D4_stddev": 0.317,
            "id":"unique_id",
            "imt":"pga",
            "imu":"g",
            "im_min":0.0,
            "im_max":1.0
        },
        {
        // ...
        },
// ...
}
```

Most important are the following meta fields:
- meta.id as it sets the schema of the fragility functions
- the meta.shape as it specifies with function to use for computing the probabilities

And the fields in the data array:
- the taxomomy field to specify the building class
- the values for mean and stddev for the different damage states
- the imt field to specify with intensity measurement it uses
- the imu field to specify the unit of the intensity measurement

The example shown above only covers the functions for the transition from
damage state 0 to the other damage states, but none in between.
Deus supports reading fragility functions also for the intermediate
transitions following this conventions:
`D -> underscore -> from damage state -> underscore -> to damage state -> underscore -> mean/stddev`
so for example `D_1_2_mean` is the mean value for the transition from damage state 1 to 2.

If deus has no state from for example `D_4_5` it will use `D_3_5`. If it hasn't this value either,
it uses `D_2_5` and so one.
Because most fragility functions will not include this intermediate values, it will map back to
the transition of `D_0_5` which must be given in the fragility function file.
(This is meant as a fallback modus).

## Shape/Function support
Currently only the log normal cdf functions are supported in deus (logncdf).

## Relationship between intensity provider and fragility functions

As the [intensity provider]{IntensityFile.md} gives dicts with the intensity values
and the units, the functions access the fields of those dicts with the key of their
own imt value.

So if the fragility funciton will use the imt value 'pga' it will access
the intensity in the following way:

```python
imt = 'pga'
intensities, units = intensity_provider.get_nearest(lon, lat)
intensity = intensities[imt]
```

The unit is checked in the same way. If there is a mismatch, so a missing intensity
or the wrong unit, deus will complain about it by throwing an exception.
