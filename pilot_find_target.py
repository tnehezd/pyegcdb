import astropy
from astropy.coordinates import SkyCoord
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from astropy.table import Table
import pandas as pd
from io import StringIO
from fastkde import pdf as fast_pdf
from scipy.interpolate import RegularGridInterpolator

hscapiurl = "https://catalogs.mast.stsci.edu/api/v0.1/hsc"

def hscsearch(table="summary", release="v3", magtype="magaper2", format="csv",
              columns=None, baseurl=hscapiurl, verbose=False, **kw):
    data = kw.copy()
    if not data:
        raise ValueError("You must specify some parameters for search")
    if format not in ("csv", "votable", "json", 'table'):
        raise ValueError("Bad value for format")
    rformat = "csv" if format == "table" else format
    url = f"{baseurl}/{release}/{table}/{magtype}.{rformat}"
    if columns:
        meta = requests.get(f"{baseurl}/{release}/{table}/{magtype}/metadata").json()
        valid = {col['name'].lower() for col in meta}
        badcols = [col for col in columns if col.lower() not in valid]
        if badcols:
            raise ValueError(f"Invalid columns: {', '.join(badcols)}")
        data['columns'] = f"[{','.join(columns)}]"
    r = requests.get(url, params=data)
    if verbose:
        print(r.url)
    r.raise_for_status()
    if format == "json":
        return r.json()
    elif format == "table":
        return Table.from_pandas(pd.read_csv(StringIO(r.text)))
    else:
        return r.text

def main():
    astropy.conf.max_width = 150
    target = 'SMC'
    coord = SkyCoord.from_name(target)
    ra, dec = coord.ra.degree, coord.dec.degree
    print(f"RA: {ra:.6f}, Dec: {dec:.6f}")

    columns = ["MatchID", "MatchRA", "MatchDec", "CI", "A_F555W", "A_F814W"]
    ddec = 1.5
    dra = ddec / np.cos(np.radians(dec))
    constraints = {
        'A_F555W_N.gte': 1, 'A_F814W_N.gte': 1,
        'CI.gt': 0.9, 'CI.lt': 1.6,
        'MatchDec.gt': dec - ddec, 'MatchDec.lt': dec + ddec,
        'MatchRA.gt': ra - dra, 'MatchRA.lt': ra + dra
    }

    t0 = time.time()
    tab = hscsearch(table="summary", release='v3', columns=columns, verbose=True,
                    pagesize=1000000, format='table', **constraints)
    print(f"{time.time()-t0:.1f}s: Retrieved {len(tab)} rows")

    tab['V-I'] = tab['A_F555W'] - tab['A_F814W']
    tab = tab[(tab['V-I'] > -1.5) & (tab['V-I'] < 1.5)]
    print(f"{time.time()-t0:.1f}s: Filtered to {len(tab)} objects with -1.5 < V-I < 1.5")

    obs = tab[['MatchRA', 'MatchDec']].to_pandas()
    obs.MatchRA = obs.MatchRA.round(0)
    obs.MatchDec = obs.MatchDec.round(2)
    print(obs.value_counts())

    x = tab['V-I']
    y = tab['A_F555W']
    myPDF, axes = fast_pdf(x, y)
    print(f"KDE completed in {time.time()-t0:.1f}s for {len(x)} points")

    finterp = RegularGridInterpolator((axes[1], axes[0]), myPDF, bounds_error=False, fill_value=0.0)
    z = finterp((y, x))
    idx = z.argsort()
    xs, ys, zs = x[idx], y[idx], z[idx]

    threshold = np.percentile(zs, 90)
    wsel = zs > threshold

    fig, ax = plt.subplots(figsize=(12, 10))
    fig.tight_layout()
    sc = ax.scatter(xs[wsel], ys[wsel], c=zs[wsel], s=2, edgecolors='none', cmap='plasma')
    ax.set(xlabel='V - I [mag]', ylabel='V [mag]',
           title=f'{len(tab):,} stars in the Small Magellanic Cloud',
           xlim=(-1.5, 1.5), ylim=(14, 27))
    ax.invert_yaxis()
    fig.colorbar(sc, ax=ax)
    plt.show()

if __name__ == "__main__":
    main()
