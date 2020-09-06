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

## TESS Stellar
def get_tess_stars_from_sector(sector_num, datapath=TESS_DATAPATH, force_redownload=False, verbose=True):
    '''
    Queries https://tess.mit.edu/observations/target-lists/ for the input catalog from TESS sector 'sector_num',
    and for each target in that list, gets its data from astroquery and joins the two catalogs.

    Arguments
    ---------
    sector_num : int
    The TESS sector number for which information is being requested.

    datapath : str
    The top-level path to which data should be stored.

    verbose : bool
    Whether to print statements on the script's progress.

    Returns
    -------
    stars : pd.DataFrame
    The joined TIC and target-list data.
    '''
    from astroquery.mast import Catalogs

    # sets up file paths and names
    sector = str(sector_num).zfill(3)
    if datapath is None:
        datapath = os.getcwd()
    if subpath is None:
        subpath = "TESS_targets_S{}.csv".format(sector)
    fullpath = os.path.join(datapath, subpath)

    if (not os.path.exists(fullpath)) or force_redownload or GLOBAL_FORCE_REDOWNLOAD:
        # queries the target list
        url = get_sector_pointings(sector_num)
        if verbose or GLOBAL_VERBOSE:
            print("Getting sector {0} observed targets from {1}.".format(sector_num, url))
        req = requests.get(url)
        if not req.ok:
            raise requests.exceptions.HTTPError("Data from sector {} is not available.".format(sector_num))
        observations = pd.read_csv(BytesIO(req.content), comment='#')[['TICID', 'Camera', 'CCD']] # MAST has Tmag, RA, Dec at higher precision
        observed_ticids = observations['TICID'].values

        # queries MAST for stellar data
        if verbose or GLOBAL_VERBOSE:
            print("Querying MAST for sector {0} observed targets.".format(sector_num))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tic_data = Catalogs.query_criteria(catalog='Tic', ID=observed_ticids).to_pandas()
        tic_data = tic_data.astype({"ID" : int})
        merged_data = tic_data.merge(observations, left_on='ID', right_on='TICID')
        noises_path = os.path.join(datapath, "TESS_noise_S{}.csv".format(sector))
        if os.path.exists(noises_path):
            merged_data = merged_data.merge(pd.read_csv(noises_path, index_col=0, comment='#'), on="ID")
        else:
            print("Noise values not found on path: change file location or download using get_tess_photometric_noise.py.")
        merged_data = merged_data.rename({"ID" : "ticid"})
        merged_data.to_csv(fullpath)
        if verbose or GLOBAL_VERBOSE:
            print("Saved TIC data from TESS sector {0} to path {1}.".format(sector_num, fullpath))
        return merged_data
    else:
        return pd.read_csv(fullpath, index_col=0)

def get_stellar_data(sectors=True, verbose=False):
    '''
    Utility function to call get_tess_stars_from_sector on a specific directory.

    Arguments
    ---------
    sectors : bool, int, or list of ints
    True for 'all available', an int for just one sector, or a list of ints for a subset of sectors.
    '''
    if sectors is True:
        i = 1
        for i in range(NUM_TESS_SECTORS):
            if verbose or GLOBAL_VERBOSE:
                print("Getting data from TESS sector {}".format(i))
            try:
                get_tess_stars_from_sector(i, datapath=TESS_DATAPATH)
            except requests.exceptions.HTTPError:
                if verbose or GLOBAL_VERBOSE:
                    print("Possibly requesting data from a nonexistent sector: run check_num_tess_sectors to ensure data exists.")
                raise
    elif isinstance(sectors, int):
        get_tess_stars_from_sector(sectors, datapath=TESS_DATAPATH)
    elif isinstance(sectors, list):
        for s in sectors:
            get_tess_stars_from_sector(s, datapath=TESS_DATAPATH)
    else:
        print("Datatype of 'sectors' not understood: set to either True, an integer, or a list of integers.")

if __name__ == "__main__":
    check_datapath()
    get_stellar_data([3, 4])