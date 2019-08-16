#TODO-List


## Mapping of taxonomies
(Exposure should contain a schema).
(Also one class can eventually be split up into several classes (for
example 50%/50%)).

(It stays that we only have to do the mapping to another schema before
the fragility computation; maybe in a later stage when we have to
compute costs we must do the back mapping to the earth quake schema,
because no data for the tsunami damage classes and the costs exists.)

(+ First is the mapping of the taxonomy then the mapping of the damage
classes; both are be independant from each other - at least what we
assume).

(maybe the mapping here is useful to match the taxonomy strings
from the fragility with those from the exposure
https://github.com/GFZ-Centre-for-Early-Warning/fuzzy_schemas/blob/master/schema_scripts/Valpo_test/Valpotest.ipynb
)
## Add reading the name of the fragility schema
## Think about having columns for damage state
(So that there is no _DXX at the end of the taxonomy).
## Check filling of damage state functions if there is one in middle
(Say from damage state 3 to 5, but no 4 to 5, so it should use the
same as 3 to 5, but 2 to 5 should still use 
## Update the testinput data
(Check assetmaster and modelprop for input data as taxonomy didn't
match in this files).
