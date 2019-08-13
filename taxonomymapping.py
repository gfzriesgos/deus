#!/usr/bin/env python3

'''
This is a module
for the mapping of the taxonomies.
'''


class TaxonomyMapper():
    '''
    This class is the taxonomy mapper.
    '''
    def __init__(self):
        pass

    def find_fragility_taxonomy_and_new_exposure_taxonomy(
            self,
            exposure_taxonomy,
            actual_damage_state,
            fragility_taxonomies):
        '''
        Finds the taxonomy for the fragility functions
        with for the given exposure taxonomy.

        Can return a different exposure taxonomy to use
        for updating the exposure file in case of
        a schema switch (as for switching from tsunamis to
        earth quake hazards).

        As on the mapping process it is also possible to
        map from one building class to another one with
        a different damage state, we also give back the
        new damage state.
        '''
        # TODO
        # here it will only take the very first fragility_taxonomy
        # and it will stay with the existing exposure_taxonomy
        # (but this may be changed in case of a different schema for
        # the fragility; this will be the case for switching to tsunami
        # fragility function).
        return (
            [*fragility_taxonomies][0],
            exposure_taxonomy,
            actual_damage_state,
        )
