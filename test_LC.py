import pandas as pd
from cepheid_client import KonkolyCepheids

db = KonkolyCepheids()

star_name = "OGLE LMC-SC1 14252"
print(f"Requesting light curve data for: {star_name}...")

lc_df = db.load_datapoints(identifier=star_name, bands=['B'])

if not lc_df.empty:
    print("\n--- Light Curve Preview ---")
    print(lc_df.head(5).to_string(index=False))
else:
    print("Failed to retrieve light curve.")