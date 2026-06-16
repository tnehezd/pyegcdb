import pandas as pd
from cepheid_client import KonkolyCepheids

# Beállítjuk a Pandast, hogy ne törje el a sorokat, és szép széles legyen a táblázat
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', lambda x: f'{x:.3f}' if isinstance(x, float) else str(x))

# 1. Kapcsolódás
db = KonkolyCepheids()

# 2. Lekérdezés
print("Fetching Large Magellanic Cloud data...")
lmc_df = db.query(galaxy="large")

# 3. Szép, formázott kiíratás
if not lmc_df.empty:

    output_filename = "lmc_cepheids.csv"
    lmc_df.to_csv(output_filename, index=False, encoding='utf-8')
    print(f"✓ Data successfully saved to: {output_filename}")

    print("\n" + "="*80)
    print("      EXTRAGALACTIC CEPHEID DATABASE - RECENTLY FETCHED RECORDS")
    print("="*80)
    
    # Kiválasztjuk a legfontosabb oszlopokat, és csak az első 10 sort íratjuk ki
    preview_cols = ['id', 'name', 'galaxy', 'type', 'period', 'ra', 'dec', 'magV']
    print(lmc_df[preview_cols].head(10).to_string(index=False))
    
    print("="*80)
    print(f"Total rows fetched: {len(lmc_df)}")
    print("="*80)

    # Egy gyors statisztika a V magnitúdókról
    print("\n--- V-Band Magnitude Distribution ---")
    print(lmc_df['magV'].describe())
else:
    print("No data returned.")