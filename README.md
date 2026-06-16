# pyegcdb

`pyegcdb` is the official Python client for the **Konkoly Cepheid Database**. It provides astronomers and researchers with a seamless interface to query light curves and stellar catalog data directly within a Python environment.

## Installation

You can install the package directly from PyPI:

```bash
pip install pyegcdb
```


## Quick Start

To begin using the library, initialize the client and fetch data by the star's name:

```python
from pyegcdb import KonkolyCepheids

# 1. Initialize the client
db = KonkolyCepheids()

# 2. Fetch light curve data for a specific star
star_name = "OGLE LMC-SC1 14252"
lc_df = db.load_datapoints(identifier=star_name, bands=['B'])

# 3. Preview the results
if not lc_df.empty:
    print(lc_df.head())
```





## Key Features

* **Light Curve Retrieval:** Easily download raw photometric time-series data for specific Cepheids.
* **Catalog Querying:** Perform advanced searches based on galaxy, variable type, or perform a Cone Search (RA/Dec).
* **Smart Filtering:** Built-in deduplication logic that prioritizes the most recent publication data.


## Citation
If you use `pyegcdb` in your research, please cite our relevant work:

```bibtex
@INPROCEEDINGS{2020svos.conf..115T,
       author = {{Tarczay-Neh{\'e}z}, D. and {Szabados}, L. and {Dencs}, Z.},
        title = "{Cepheids Near and Far}",
     keywords = {Stars: variables: Cepheids, Astronomical databases: miscellaneous, Galaxies: statistics, Stars: statistics, Galaxy: stellar content, (Cosmology:) distance scale},
    booktitle = {Stars and their Variability Observed from Space},
         year = 2020,
       editor = {{Neiner}, C. and {Weiss}, W.~W. and {Baade}, D. and {Griffin}, R.~E. and {Lovekin}, C.~C. and {Moffat}, A.~F.~J.},
        month = jan,
        pages = {115-118},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2020svos.conf..115T},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}



@INPROCEEDINGS{2022eas..conf..420T,
       author = {{Tarczay-Neh{\'e}z}, D{\'o}ra and {Dencs}, Zolt{\'a}n and {Szabados}, L{\'a}szl{\'o} and {Moln{\'a}r}, L{\'a}szl{\'o}},
        title = "{Extragalactic Cepheid Database}",
    booktitle = {EAS2022, European Astronomical Society Annual Meeting},
         year = 2022,
        month = jul,
          eid = {420},
        pages = {420},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2022eas..conf..420T},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}



```


## License
This software is released under the [GNU GPLv3] license.
