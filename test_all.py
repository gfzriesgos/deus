#!/usr/bin/env python3

# Copyright © 2021-2022 Helmholtz Centre Potsdam GFZ German Research Centre for
# Geosciences, Potsdam, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Unit tests for all basic functions
"""
import unittest

# import other test classes
from test_basics import *
from test_ashfall import *
from test_cmdexecution import *
from test_fragility import *
from test_gpdexposure import *
from test_intensity import *
from test_intensitydatawrapper import *
from test_loss import *
from test_performance import *
from test_schemamapping import *
from test_shakemap import *


if __name__ == "__main__":
    unittest.main()
