## Utilities to get stellar parameters

import os
import requests
import pandas as pd
import warnings
from astroquery.mast import Catalogs
from io import BytesIO

import utils

def get_tess_stars_from_sector(sector_num, datapath=utils.TESS_DATAPATH, force_redownload=False, verbose=True):
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
    # sets up file paths and names
    sector = str(sector_num).zfill(3)
    if datapath is None:
        datapath = os.getcwd()
    subpath = "tesstargets" + os.path.sep + "TESS_targets_S{}.csv".format(sector)
    fullpath = os.path.join(datapath, subpath)
    noises_path = os.path.join(datapath, "tess_photometric_noise" + os.path.sep + "TESS_noise_S{}.csv".format(sector))

    if (not os.path.exists(fullpath)) or force_redownload or utils.GLOBAL_FORCE_REDOWNLOAD:
        # queries the target list
        url = utils.get_sector_pointings(sector_num)
        if verbose or utils.GLOBAL_VERBOSE:
            print("Getting sector {0} observed targets from {1}.".format(sector_num, url))
        req = requests.get(url)
        if not req.ok:
            raise requests.exceptions.HTTPError("Data from sector {} is not available.".format(sector_num))
        observations = pd.read_csv(BytesIO(req.content), comment='#')[['TICID', 'Camera', 'CCD']] # MAST has Tmag, RA, Dec at higher precision
        observed_ticids = observations['TICID'].values

        # queries MAST for stellar data
        if verbose or utils.GLOBAL_VERBOSE:
            print("Querying MAST for sector {0} observed targets.".format(sector_num))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tic_data = Catalogs.query_criteria(catalog='Tic', ID=observed_ticids).to_pandas()
        tic_data = tic_data.astype({"ID" : int})
        merged_data = tic_data.merge(observations, left_on='ID', right_on='TICID')
        if os.path.exists(noises_path):
            merged_data = merged_data.merge(pd.read_csv(noises_path, index_col=0, comment='#'), on="ID")
        else:
            print("Noise values not found on path: change file location or download using get_tess_photometric_noise.py.")
        merged_data = merged_data.rename({"ID" : "ticid"})
        merged_data.to_csv(fullpath)
        if verbose or utils.GLOBAL_VERBOSE:
            print("Saved TIC data from TESS sector {0} to path {1}.".format(sector_num, fullpath))
        return merged_data
    else:
        stellar_sector_data = pd.read_csv(fullpath, index_col=0)
        if "noise" not in stellar_sector_data.index and os.path.exists(noises_path):
            stellar_sector_data = stellar_sector_data.merge(pd.read_csv(noises_path, index_col=0, comment='#'), on="ID")
            stellar_sector_data.to_csv(fullpath)
            if verbose or utils.GLOBAL_VERBOSE:
                print("Added photometric noise values to TIC data from TESS sector {0} to path {1}.".format(sector_num, fullpath))
        return stellar_sector_data

def get_tess_stars_multiple_sectors(sectors=True, verbose=False):
    '''
    Utility function to call get_tess_stars_from_sector on a specific directory.

    Arguments
    ---------
    sectors : bool, int, or list of ints
    True for 'all available', an int for just one sector, or a list of ints for a subset of sectors.
    '''
    if sectors is True:
        i = 1
        for i in range(utils.NUM_TESS_SECTORS):
            if verbose or utils.GLOBAL_VERBOSE:
                print("Getting data from TESS sector {}".format(i))
            try:
                get_tess_stars_from_sector(i, datapath=utils.TESS_DATAPATH)
            except requests.exceptions.HTTPError:
                if verbose or utils.GLOBAL_VERBOSE:
                    print("Possibly requesting data from a nonexistent sector: run utils.check_num_tess_sectors to ensure data exists.")
                raise
    elif isinstance(sectors, int):
        get_tess_stars_from_sector(sectors, datapath=utils.TESS_DATAPATH)
    elif isinstance(sectors, list):
        for s in sectors:
            get_tess_stars_from_sector(s, datapath=utils.TESS_DATAPATH)
    else:
        print("Datatype of 'sectors' not understood: set to either True, an integer, or a list of integers.")

def get_tess_stellar_catalog(sectors=None, unique=True, force_resave=False, force_redownload=False):
    '''
    Wrapper around tess_target_stars.py to merge all sectors into one catalog.

    Arguments
    ---------
    sectors : list
    A list of sector IDs to query.

    unique : bool
    If true, this function cuts down the stellar dataframe to only unique entries, and adds a few columns.

    force_resave : bool
    If true, forces a reread of the constituent files from the URL (rerun of get_tess_stars_from_sector)

    Returns
    -------
    stlr : pd.DataFrame
    The stellar dataframe. If `unique`, the returned value is instead:

    stlr : pd.DataFrame
    The stellar dataframe, with duplicates dropped and the following columns added:
        sectors, str      : the sectors in which the target was observed.
        noise, str        : the 1-hour photometric noise of the observation in each sector
    '''
    if sectors is None:
        sectors = list(range(1, NUM_TESS_SECTORS + 1))
    frames = []
    sector_obs = {}
    sector_cnt = {}
    noises = {}
    for s in sectors:
        datapath = os.path.join(TESS_DATAPATH, "TESS_targets_S{}.csv".format(str(s).zfill(3)))
        if os.path.exists(datapath) and (not force_resave):
            df = pd.read_csv(datapath, comment='#', index_col=0)
        else:
            df = get_tess_stars_from_sector(s, force_redownload=force_redownload)
        if unique:
            for ticid, noise in zip(df["ticid"].values, df["noise"].values):
                if ticid not in sector_obs:
                    sector_obs[ticid] = str(s)
                    sector_cnt[ticid] = 1
                    noises[ticid] = str(noise)
                else:
                    sector_obs[ticid] += ',' + str(s)
                    sector_cnt[ticid] += 1
                    noises[ticid] += ',' + str(noise)
        frames.append(df)
    stlr = pd.concat(frames)
    if unique:
        stlr.drop_duplicates(subset="ticid", inplace=True)
        stlr["sectors"] = [sector_obs.get(ticid) for ticid in stlr["ticid"].values]
        stlr["noise"] = [noises.get(ticid) for ticid in stlr["ticid"].values]
        # stlr["dataspan"] = 27.4 * np.array([sector_cnt.get(ticid) for ticid in stlr["ticid"].values])
        # stlr["dutycycle"] = 13.0/13.7 * np.ones_like(stlr["dataspan"])
    return stlr
