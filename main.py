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
tesspoint = importlib.import_module("tess-point")
import lightkurve as lk

import utils, stellar

if __name__ == "__main__":
    stellar.get_tess_stars_from_sector(5)