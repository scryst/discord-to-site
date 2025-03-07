import requests
import json
import time
import os
from datetime import datetime

# Configuration
RENDER_API_URL = "https://discord-to-site-api.onrender.com"

def check_api_health():
    """Check if the API is healthy and get detailed information"""
    try:
        response = requests.get(f"{RENDER_API_URL}/api/health")
        print(f"API Health Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: {data.get('status')}")
            print(f"Bot Running: {data.get('bot_running')}")
            print(f"Export Directory Exists: {data.get('export_dir_exists')}")
            
            export_files = data.get('export_files', [])
            print(f"Export Files Count: {len(export_files)}")
            
            if export_files:
                print("Export Files:")
                for file in export_files:
                    print(f"  - {file}")
            else:
                print("No export files found")
                
            return data
        return None
    except Exception as e:
        print(f"Error checking API health: {e}")
        return None

def trigger_export():
    """Trigger a Discord data export on Render"""
    try:
        print("\n=== Triggering Export ===")
        response = requests.post(f"{RENDER_API_URL}/api/trigger_export")
        print(f"Trigger Export Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            return True
        else:
            print(f"Failed to trigger export: {response.text}")
            return False
    except Exception as e:
        print(f"Error triggering export: {e}")
        return False

def check_summary():
    """Check if a summary file exists"""
    try:
        print("\n=== Checking Summary ===")
        response = requests.get(f"{RENDER_API_URL}/api/summary")
        print(f"Summary Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                print(f"Error: {data.get('error')}")
                print(f"Status: {data.get('status')}")
                return False
            
            print(f"Server Name: {data.get('server_name')}")
            print(f"Export Time: {data.get('export_time')}")
            
            if "files" in data:
                print("Files:")
                for key, value in data.get('files', {}).items():
                    print(f"  - {key}: {value}")
            
            return True
        else:
            print(f"Failed to get summary: {response.text}")
            return False
    except Exception as e:
        print(f"Error checking summary: {e}")
        return False

def check_data():
    """Check if the API is returning data"""
    try:
        print("\n=== Checking All Data ===")
        response = requests.get(f"{RENDER_API_URL}/api/all")
        print(f"Data Check Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        
        if "error" in data:
            print(f"Error: {data.get('error')}")
            print(f"Status: {data.get('status')}")
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

def main():
    """Main function"""
    print("=== Discord Export Debugging Tool ===")
    print(f"Target API: {RENDER_API_URL}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check API health
    print("\n=== Step 1: Checking API Health ===")
    health_data = check_api_health()
    
    if not health_data:
        print("API health check failed")
        return
    
    # Step 2: Trigger export
    print("\n=== Step 2: Triggering Export ===")
    if not trigger_export():
        print("Failed to trigger export")
        return
    
    # Step 3: Wait and check for data
    print("\n=== Step 3: Waiting for Export to Complete ===")
    max_attempts = 10
    wait_time = 10  # seconds
    
    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt}/{max_attempts} - Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
        # Check health again to see if files have been created
        health_data = check_api_health()
        
        if health_data and health_data.get('export_files'):
            print("Export files detected!")
            break
    
    # Step 4: Check summary
    print("\n=== Step 4: Checking Summary ===")
    summary_exists = check_summary()
    
    # Step 5: Check all data
    print("\n=== Step 5: Checking All Data ===")
    data_exists = check_data()
    
    # Final report
    print("\n=== Final Report ===")
    print(f"API Health: {'OK' if health_data else 'FAILED'}")
    print(f"Export Files: {len(health_data.get('export_files', [])) if health_data else 0}")
    print(f"Summary Exists: {'YES' if summary_exists else 'NO'}")
    print(f"Data Available: {'YES' if data_exists else 'NO'}")
    
    if not data_exists:
        print("\n=== Troubleshooting Suggestions ===")
        print("1. Check if the Discord bot has the necessary permissions")
        print("2. Check if the Discord token is set correctly in the environment variables")
        print("3. Check the server logs for any errors during the export process")
        print("4. Try restarting the server and then running this script again")
        print("5. Make sure the server_data directory is writable")

if __name__ == "__main__":
    main()
