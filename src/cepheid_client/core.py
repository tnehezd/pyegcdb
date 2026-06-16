import requests

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
            # We send a standard GET request with a 5-second timeout
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