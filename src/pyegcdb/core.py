import requests
import pandas as pd
import urllib.parse

class KonkolyCepheids:
    def __init__(self, base_url="https://cepheids.konkoly.hu/api/v1"):
        self.base_url = base_url
        self._band_map = {
            1: 'magU', 2: 'magB', 3: 'magV', 4: 'magR', 5: 'magI', 6: 'magJ', 7: 'magH', 8: 'magK',
            9: 'magu', 10: 'magg', 11: 'magr', 12: 'magi', 13: 'magz', 14: 'magG',
            46: 'magW1', 47: 'magW2', 48: 'magW3', 49: 'magW4'
        }

    def ping(self) -> bool:
        url = f"{self.base_url}/ping"
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def query(self, 
              galaxy: str = None, 
              var_type: int = None, 
              ra: str or float = None,
              dec: str or float = None,
              radius: float or int = 5,
              bands: str or list = 'all', 
              include_period: bool = True) -> pd.DataFrame:
        """
        Queries the database with support for galaxy, type, and Cone Search (RA/Dec).
        Filters out database-level duplicates by keeping the newest publication data.
        """
        url = f"{self.base_url}/cepheids"
        
        params = {
            'include_period': str(include_period).lower()
        }
        if galaxy:
            params['galaxy'] = galaxy
        if var_type:
            params['type'] = var_type
            
        if ra is not None and dec is not None:
            params['ra'] = str(ra)
            params['dec'] = str(dec)
            params['radius'] = float(radius)

        if isinstance(bands, list):
            params['bands'] = ",".join(bands)
        else:
            params['bands'] = bands

        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                print(f"❌ Server error: {response.status_code}")
                return pd.DataFrame()

            json_data = response.json()
            if json_data.get('status') != 'success' or json_data.get('count', 0) == 0:
                print("⚠ No records found matching the criteria.")
                return pd.DataFrame()

            raw_data = json_data['data']
            flattened_records = []

            for item in raw_data:
                # Kinyerjük a pozíciókat, hogy meghatározzuk a legfrissebbet (legnagyobb art_id)
                positions = item.get('positions', [])
                base2 = [p for p in positions if p.get('base') == 2]
                
                latest_pos = None
                latest_art_id = -1
                
                if base2:
                    # Megkeressük a legfrissebb pozíció rekordot az art_id alapján
                    latest_pos = sorted(base2, key=lambda x: x.get('art_id', 0) or 0, reverse=True)[0]
                    latest_art_id = latest_pos.get('art_id', 0) or 0

                gal = item.get('galaxy')

                if isinstance(gal, dict):
                    galaxy_name = gal.get('name')
                else:
                    galaxy_name = None

                record = {
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'galaxy': galaxy_name,
                    'type': item.get('types', [{}])[0].get('type') if item.get('types') else None,
                    'latest_art_id': latest_art_id
                }

                if 'distance_arcsec' in item:
                    record['distance_arcsec'] = float(item['distance_arcsec'])

                if include_period:
                    periods = item.get('periods', [])
                    record['period'] = float(periods[0].get('value')) if periods and periods[0].get('value') else None

                if latest_pos:
                    record['ra'] = latest_pos.get('ra')
                    record['dec'] = latest_pos.get('dec')
                else:
                    record['ra'] = record['dec'] = None

                if isinstance(bands, list):
                    for b in bands:
                        record[f'mag{b}'] = None
                else:
                    for b_name in self._band_map.values():
                        record[b_name] = None

                for mag_obj in item.get('magnitudes', []):
                    b_id = mag_obj.get('band_type_id')
                    b_col_name = self._band_map.get(b_id)
                    if b_col_name:
                        record[b_col_name] = float(mag_obj.get('value')) if mag_obj.get('value') else None

                flattened_records.append(record)

            df = pd.DataFrame(flattened_records)
            
            # --- DUPLIKÁCIÓK TISZTÍTÁSA CIKK-FRISSESSÉG ALAPJÁN ---
            if not df.empty:
                # Először a legfrissebb cikkek szerint csökkenőbe rendezünk
                df = df.sort_values('latest_art_id', ascending=False)
                
                # Csillag ID alapján eldobjuk a duplikátumokat, így a legfrissebb (első) marad meg
                df = df.drop_duplicates(subset=['id'], keep='first')
                
                # Ha volt Cone Search, akkor esztétikailag visszaállíthatjuk a távolság szerinti sorrendet
                if 'distance_arcsec' in df.columns:
                    df = df.sort_values('distance_arcsec')
                    
                # Takarítás: a segéd oszlopot elrejtjük a kutató elől
                df = df.drop(columns=['latest_art_id']).reset_index(drop=True)

            print(f"✓ Successfully fetched and cleaned {len(df)} unique records (based on latest publication).")
            return df

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return pd.DataFrame()

    def load_datapoints(self, identifier: int or str, bands: str or list = 'all') -> pd.DataFrame:
        """
        Fetches the raw photometric time-series (light curve) for a specific Cepheid.
        """
        safe_identifier = urllib.parse.quote(str(identifier))
        url = f"{self.base_url}/cepheids/{safe_identifier}/lightcurve"

        params = {}
        if isinstance(bands, list):
            params['bands'] = ",".join(bands)
        else:
            params['bands'] = bands

        local_band_map = {
            1: 'U', 2: 'B', 3: 'V', 4: 'R', 5: 'I', 6: 'J', 7: 'H', 8: 'K',
            9: 'u', 10: 'g', 11: 'r', 12: 'i', 13: 'z', 14: 'G',
            46: 'W1', 47: 'W2', 48: 'W3', 49: 'W4'
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            
            #DEBUG: Ha 500-as hiba van, írjuk ki, mit mondott a szerver
            if response.status_code == 500:
                print(f"❌ Server error 500! Szerver válasza: {response.text[:500]}")
                return pd.DataFrame()
            elif response.status_code != 200:
                print(f"❌ Server error: {response.status_code}")
                return pd.DataFrame()

            json_data = response.json()
            if json_data.get('status') != 'success':
                print(f"❌ Database error: {json_data.get('message', 'Unknown error')}")
                return pd.DataFrame()

            server_ceph_id = json_data.get('ceph_id')
            server_star_name = json_data.get('name')
            print(f"🎯 Star resolved: Found '{server_star_name}' (Internal EGCDb ID: {server_ceph_id})")
            
            raw_points = json_data['data']
            total_points = json_data.get('count', 0)
            
            if total_points == 0:
                print(f"⚠ Warning: No points found matching the criteria.")
                return pd.DataFrame()

            print(f"📥 Downloading and parsing {total_points} photometric datapoints...")

            flattened_points = []
            for pt in raw_points:
                b_id = pt.get('ceph_mag_conn_id')
                b_name = local_band_map.get(b_id, f"ID_{b_id}")

                jd_val = pt.get('time_jd') if pt.get('time_jd') is not None else pt.get('HJD_epoch')

                flattened_points.append({
                    'jd': float(jd_val) if jd_val is not None else None,
                    'magnitude': float(pt['data']) if pt.get('data') is not None else None,
                    'error': float(pt['mag_err']) if pt.get('mag_err') is not None else None,
                    'band': b_name
                })

            df = pd.DataFrame(flattened_points)
            if not df.empty and 'jd' in df.columns:
                df = df.sort_values('jd').reset_index(drop=True)
                
            print(f"✓ Light curve loaded successfully into DataFrame.")
            return df

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error while fetching light curve: {e}")
            return pd.DataFrame()