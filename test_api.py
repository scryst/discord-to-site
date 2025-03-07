import requests
import time
import json

# Configuration
API_URL = "https://discord-to-site-api.onrender.com"

def check_health():
    """Check the health of the API"""
    try:
        response = requests.get(f"{API_URL}/api/health")
        print(f"Health check: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error checking health: {e}")
        return False

def trigger_export():
    """Trigger a Discord data export"""
    try:
        response = requests.post(f"{API_URL}/api/trigger_export")
        print(f"Trigger export: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Error triggering export: {e}")
        return False

def check_data():
    """Check if the API is returning data"""
    try:
        response = requests.get(f"{API_URL}/api/all")
        print(f"Data check: {response.status_code}")
        data = response.json()
        
        if "error" in data and data.get("status") == "waiting_for_data":
            print("No data available yet")
            return False
        
        # Print a summary of the data
        if "summary" in data:
            print(f"Server: {data['summary'].get('server_name')}")
            print(f"Export time: {data['summary'].get('export_time')}")
        
        if "members" in data and isinstance(data["members"], list):
            print(f"Members: {len(data['members'])}")
        
        if "channels" in data and isinstance(data["channels"], list):
            print(f"Channels: {len(data['channels'])}")
        
        if "roles" in data and isinstance(data["roles"], list):
            print(f"Roles: {len(data['roles'])}")
        
        return True
    except Exception as e:
        print(f"Error checking data: {e}")
        return False

if __name__ == "__main__":
    print("Testing Discord to Site API...")
    
    # Check health
    print("\n=== Health Check ===")
    if not check_health():
        print("Health check failed")
    
    # Trigger export
    print("\n=== Triggering Export ===")
    if trigger_export():
        print("Export triggered successfully")
    else:
        print("Failed to trigger export")
    
    # Wait for export to complete
    print("\n=== Waiting for export to complete ===")
    for i in range(5):
        print(f"Checking data (attempt {i+1}/5)...")
        if check_data():
            print("Data is available!")
            break
        time.sleep(5)
    
    print("\nTest completed")
