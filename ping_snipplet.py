import sys
from pyegcdb import KonkolyCepheids

def connect_to_database():
    """
    Initializes the Konkoly Cepheid database client 
    and verifies the connection to the remote server.
    """
    print("Connecting to the Konkoly Cepheid Database...")
    
    try:
        # Initialize the client (defaults to the production API URL)
        db = KonkolyCepheids()
        
        # Verify the server connection via heartbeat ping
        if db.ping():
            print("Successfully connected to Konkoly EGCDB server!")
            return db
        else:
            print("Server is reachable, but returned a connection error.")
            return None
            
    except Exception as e:
        print(f"Connection failed: {e}", file=sys.stderr)
        return None

# --- Execution ---
if __name__ == "__main__":
    db = connect_to_database()
    
    if db:
        print("The 'db' object is ready for data queries.")
