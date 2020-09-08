# General-purpose utilities, such as getting/filling URLs and local datapaths.

import os
import requests

# globals
TESS_DATAPATH = os.path.abspath(os.getcwd()) + "/data/" # or change to any other desired path
assert TESS_DATAPATH[-1] == os.path.sep, "must end datapath with {}".format(os.path.sep)
NUM_TESS_SECTORS = 27
GLOBAL_VERBOSE = True # whether to print statements about script progress
GLOBAL_FORCE_REDOWNLOAD = False # whether to force data products to redownload from source, e.g. if more TOIs have been released

# utility lambdas for filling URLs
get_sector_pointings = lambda sector: 'https://tess.mit.edu/wp-content/uploads/all_targets_S{}_v1.csv'.format(str(sector).zfill(3))
get_toi_url = lambda catalog_source: {
        "caltech" : "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=toi",
        "mit" : "https://tev.mit.edu/data/collection/193/csv/6/"
    }.get(catalog_source)

# checks
def check_datapath():
    if not os.path.isdir(TESS_DATAPATH):
        if GLOBAL_VERBOSE:
            print("Making datapath at {}".format(TESS_DATAPATH))
        os.makedirs(TESS_DATAPATH, exist_ok=True)

def check_num_tess_sectors():
    i = 1
    has_data = True
    while has_data:
        url = 'https://tess.mit.edu/wp-content/uploads/all_targets_S{}_v1.csv'.format(str(i).zfill(3))
        r = requests.get(url)
        has_data = r.ok
        if has_data:
            i += 1
    if i - 1 != NUM_TESS_SECTORS:
        print("NUM_TESS_SECTORS is listed as {0}, but data was found for {1} sectors: update the variable NUM_TESS_SECTORS for the full data.".format(NUM_TESS_SECTORS, i))
