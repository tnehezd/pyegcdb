import requests
import pandas as pd

class KonkolyCepheids:
    def __init__(self, base_url="https://cepheids.konkoly.hu/api/v1"):
        self.base_url = base_url

    def ping(self) -> bool:
        """
        Verifies if the Konkoly Cepheid server is reachable.
        Returns True if online, False otherwise.
        """
        url = f"{self.base_url}/ping"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Connection successful! Server message: {data['message']}")
                return True
            else:
                print(f"Server responded, but with an error code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Could not reach the server. Error: {e}")
            return False

    def query(self, galaxy: str = None, var_type: int = None) -> pd.DataFrame:
            """
            Queries the Konkoly Cepheid Database and returns a flattened Pandas DataFrame.
            """
            url = f"{self.base_url}/cepheids"
            
            params = {}
            if galaxy:
                params['galaxy'] = galaxy
            if var_type:
                params['type'] = var_type

            try:
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    json_data = response.json()
                    
                    if json_data.get('status') == 'success' and json_data.get('count', 0) > 0:
                        raw_data = json_data['data']
                        
                        flattened_records = []
                        for item in raw_data:
                            # Alapadatok kigyűjtése
                            record = {
                                'id': item.get('id'),
                                'name': item.get('name'),
                                'galaxy': item.get('galaxy', {}).get('gen_short_name', 'Unknown'),
                            }
                            
                            # 1. Periódus kinyerése a relációból (periods listából)
                            periods = item.get('periods', [])
                            if periods:
                                record['period'] = float(periods[0].get('value')) if periods[0].get('value') else None
                            else:
                                record['period'] = None
                            
                            # 2. Pozíció kinyerése (az első base=2 pozíciót vesszük)
                            positions = item.get('positions', [])
                            base2_positions = [p for p in positions if p.get('base') == 2]
                            if base2_positions:
                                latest_pos = sorted(base2_positions, key=lambda x: x.get('art_id', 0), reverse=True)[0]
                                record['ra'] = latest_pos.get('ra')
                                record['dec'] = latest_pos.get('dec')
                                record['ra_deg'] = latest_pos.get('ra_deg_decimal')
                                record['dec_deg'] = latest_pos.get('dec_decimal')
                            else:
                                record['ra'] = record['dec'] = record['ra_deg'] = record['dec_deg'] = None

                            # 3. Változékonysági típus kinyerése
                            types = item.get('types', [])
                            if types:
                                record['type'] = types[0].get('type')
                            else:
                                record['type'] = None

                            # 4. Magnitúdók kinyerése (V-sáv [band_type_id=3])
                            magnitudes = item.get('magnitudes', [])
                            v_mags = [m for m in magnitudes if m.get('band_type_id') == 3]
                            if v_mags:
                                record['magV'] = float(v_mags[0].get('value')) if v_mags[0].get('value') else None
                            else:
                                record['magV'] = None

                            flattened_records.append(record)

                        df = pd.DataFrame(flattened_records)
                        print(f"Successfully fetched and flattened {len(df)} records.")
                        return df
                    else:
                        print("No records found or empty database response.")
                        return pd.DataFrame()
                else:
                    print(f"Server error: {response.status_code}")
                    return pd.DataFrame()
                    
            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}")
                return pd.DataFrame()
            

    def load_datapoints(self, identifier: int or str, bands: str or list = 'all') -> pd.DataFrame:
            """
            Fetches the raw photometric time-series (light curve) for a specific Cepheid.
            Allows filtering by specific photometric bands.
            """
            import urllib.parse
            safe_identifier = urllib.parse.quote(str(identifier))
            url = f"{self.base_url}/cepheids/{safe_identifier}/lightcurve"

            # GET paraméterek összeállítása a sávokhoz
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
                
                if response.status_code == 404:
                    print(f"❌ Error: Cepheid '{identifier}' does not exist in the database.")
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