## Get TOI catalogs from either the Caltech or MIT TOI list.

import os
import requests
import warnings
import numpy as np
import pandas as pd
from functools import reduce
from io import BytesIO

import utils

catalog_source = "caltech" # or "mit"; Caltech refers to the Exoplanet Archive, MIT refers to https://tev.mit.edu/data/.

def get_tois(catalog_source=catalog_source, force_redownload=False):
    '''
    Request a pandas dataframe of all the TESS objects of interest.
    '''
    url = utils.get_toi_url(catalog_source)

    fullpath = os.path.join(utils.TESS_DATAPATH, "toi" + os.path.sep + "toi_catalog_{}.csv".format(catalog_source))
    if (not force_redownload) and os.path.exists(fullpath):
        return pd.read_csv(fullpath, comment='#')
    else:
        print("Retrieving TOI table from {}.".format(url))
        req = requests.get(url)
        tois = pd.read_csv(BytesIO(req.content), comment='#', index_col=0)
        if catalog_source == "mit":
            tois = tois.rename(columns={
                "Source Pipeline" : "pipeline",
                "Full TOI ID" : "toi_id",
                "TOI Disposition" : "toi_pdisposition",
                "TIC Right Ascension" : "tic_ra",
                "TIC Declination" : "tic_dec",
                "TMag Value" : "tmag", 
                "TMag Uncertainty" : "tmag_err", 
                "Orbital Epoch Value" : "epoch",
                "Orbital Epoch Error" : "epoch_err",
                "Orbital Period Value" : "toi_period",
                "Orbital Period Error" : "toi_period_err",
                "Transit Duration Value" : "toi_transit_dur",
                "Transit Duration Error" : "toi_transit_dur_err",
                "Transit Depth Value" : "toi_transit_depth",
                "Transit Depth Error" : "toi_transit_depth_err",
                "Sectors" : "sectors",
                "Public Comment" : "comment",
                "Surface Gravity Value" : "surface_grav",
                "Surface Gravity Uncertainty" : "surface_grav_err",
                "Signal ID" : "signal_id",
                "Star Radius Value" : "srad",
                "Star Radius Error" : "srad_err",
                "Planet Radius Value" : "toi_prad",
                "Planet Radius Error" : "toi_prad_err",
                "Planet Equilibrium Temperature (K) Value" : "ptemp",
                "Effective Temperature Value" : "steff",
                "Effective Temperature Uncertainty" : "steff_err",
                "Effective Stellar Flux Value" : "sflux",
                "Signal-to-noise" : "snr",
                "Centroid Offset" : "centroid_offset",
                "TFOP Master" : "tfop_master", 
                "TFOP SG1a" : "tfop_sg1a", 
                "TFOP SG1b" : "tfop_sg1b", 
                "TFOP SG2" : "tfop_sg2", 
                "TFOP SG3" : "tfop_sg3",
                "TFOP SG4" : "tfop_sg4", 
                "TFOP SG5" : "tfop_sg5", 
                "Alerted" : "alerted", 
                "Updated" : "updated"
            })
        tois.to_csv(fullpath)
        return tois