import pandas as pd
from cepheid_client import KonkolyCepheids

db = KonkolyCepheids()

ra_target = "05:32:57.60"
dec_target = "-70:22:35.70"
search_radius_arcsec = 1000

print(f"Running Cone Search around RA={ra_target}, Dec={dec_target} (Radius: {search_radius_arcsec} arcsec)...")

df_cone = db.query(ra=ra_target, dec=dec_target, radius=search_radius_arcsec, bands=['B', 'V'])

if not df_cone.empty:
    print("\n--- Cone Search Results (Sorted by proximity) ---")
    display_cols = ['id', 'name', 'galaxy', 'ra', 'dec', 'magV']
    if 'distance_arcsec' in df_cone.columns:
        display_cols.insert(2, 'distance_arcsec')
        
    print(df_cone[display_cols].to_string(index=False))
else:
    print("No stars found within the specified cone.")