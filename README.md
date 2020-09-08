# TESS Data Products
A collection of utilities to get TESS data products from all their different homes across the web!

![](https://imgs.xkcd.com/comics/standards.png)

By running the functions here, the directory ./data/ (or any other target directory specified in utils.py's TESS_DATAPATH parameter) will be populated with:

- stellar parameter data from astroquery.mast, by sector or in aggregate (stellar.py)
- planetary parameter data from the Caltech or MIT lists of TOIs (planetary.py)
- TESS full-frame images and light curves, thinly wrapping around the 'eleanor' package, exposing some top-level parameters and handling the data paths (ffi.py and lightcurve.py)
