#!/usr/bin/env python3

import os
from deus import *

def test_all_imports_are_ok():
    import scipy as sp
    import lxml.etree as le

def test_load_exposure_cell_iterable():
    filename = './testinputs/exposure.json'
    output = load_exposure_cell_iterable(filename)

