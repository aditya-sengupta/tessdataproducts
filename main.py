'''
A common interface to access all kinds of TESS data!

Provides the following functions:

get_tess_stars_from_sector: gets stellar parameters for every star observed in a certain TESS sector.

'''
# imports
import os
import requests
import warnings
import numpy as np
import pandas as pd
from io import BytesIO
import importlib
tesspoint_function = importlib.import_module("tess-point.tess_stars2px").tess_stars2px_function_entry
import lightkurve as lk

import src.ffi as ffi
import src.lightcurve as lightcurve
import src.planetary as planetary
import src.stellar as stellar
import src.utils as utils

if __name__ == "__main__":
    planetary.get_tois("caltech")