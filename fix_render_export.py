import os
import json
import requests
import time
from datetime import datetime

# Configuration
RENDER_API_URL = "https://discord-to-site-api.onrender.com"
LOCAL_SERVER_DATA_DIR = "server_data"

def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{RENDER_API_URL}/api/health")
        print(f"API Health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API Status: {data.get('status')}")
            print(f"Bot Running: {data.get('bot_running')}")
            print(f"Export Directory Exists: {data.get('export_dir_exists')}")
            export_files = data.get('export_files', [])
            print(f"Export Files: {export_files}")
            return data
        return None
    except Exception as e:
        print(f"Error checking API health: {e}")
        return None

def create_manual_export_files():
    """Create export files manually using local data"""
    print("\n=== Creating Manual Export Files ===")
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Check if local server_data directory exists
    if not os.path.exists(LOCAL_SERVER_DATA_DIR):
        print(f"Error: Local server_data directory not found: {LOCAL_SERVER_DATA_DIR}")
        return False
    
    # Find all JSON files in the local server_data directory
    json_files = [f for f in os.listdir(LOCAL_SERVER_DATA_DIR) if f.endswith('.json')]
    
    if not json_files:
        print("Error: No JSON files found in local server_data directory")
        return False
    
    print(f"Found {len(json_files)} JSON files in local server_data directory")
    
    # Group files by timestamp
    file_groups = {}
    for filename in json_files:
        parts = filename.split('_')
        if len(parts) >= 3:
            file_type = parts[0]
            timestamp_part = f"{parts[1]}_{parts[2].split('.')[0]}"
            
            if timestamp_part not in file_groups:
                file_groups[timestamp_part] = []
            
            file_groups[timestamp_part].append((file_type, filename))
    
    # Find the most complete group
    most_complete_timestamp = None
    most_complete_count = 0
    
    for timestamp_part, files in file_groups.items():
        if len(files) > most_complete_count:
            most_complete_count = len(files)
            most_complete_timestamp = timestamp_part
    
    if not most_complete_timestamp:
        print("Error: Could not find a complete set of export files")
        return False
    
    print(f"Using timestamp: {most_complete_timestamp}")
    print(f"Files in this group: {file_groups[most_complete_timestamp]}")
    
    # Create a dictionary of file types to file paths
    files_dict = {}
    for file_type, filename in file_groups[most_complete_timestamp]:
        local_path = os.path.join(LOCAL_SERVER_DATA_DIR, filename)
        files_dict[file_type] = local_path
    
    # Create a summary file
    summary = {
        "server_name": "Coffee Chat Ventures",
        "server_id": "123456789012345678",
        "export_time": datetime.now().isoformat(),
        "files": files_dict
    }
    
    # Save the summary file locally
    summary_filename = f"summary_{timestamp}.json"
    summary_path = os.path.join(LOCAL_SERVER_DATA_DIR, summary_filename)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Created local summary file: {summary_path}")
    
    # Upload all files to Render
    return upload_files_to_render(files_dict, summary_path)

def upload_files_to_render(files_dict, summary_path):
    """Upload files to Render"""
    print("\n=== Uploading Files to Render ===")
    
    # Create the server_data directory on Render
    try:
        response = requests.post(f"{RENDER_API_URL}/api/create_directory")
        print(f"Create directory response: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to create directory: {response.text}")
            return False
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False
    
    # Upload each file
    success_count = 0
    total_files = len(files_dict) + 1  # +1 for the summary file
    
    # Upload data files
    for file_type, file_path in files_dict.items():
        try:
            print(f"Uploading {file_path}...")
            with open(file_path, 'rb') as file:
                filename = os.path.basename(file_path)
                response = requests.post(
                    f"{RENDER_API_URL}/api/upload_file", 
                    files={'file': (filename, file, 'application/json')}
                )
                
                if response.status_code == 200:
                    print(f"Successfully uploaded {filename}")
                    success_count += 1
                else:
                    print(f"Failed to upload {filename}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error uploading {file_path}: {e}")
    
    # Upload summary file
    try:
        print(f"Uploading {summary_path}...")
        with open(summary_path, 'rb') as file:
            filename = os.path.basename(summary_path)
            response = requests.post(
                f"{RENDER_API_URL}/api/upload_file", 
                files={'file': (filename, file, 'application/json')}
            )
            
            if response.status_code == 200:
                print(f"Successfully uploaded {filename}")
                success_count += 1
            else:
                print(f"Failed to upload {filename}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error uploading {summary_path}: {e}")
    
    print(f"Successfully uploaded {success_count} out of {total_files} files")
    return success_count == total_files

def check_data():
    """Check if the API is returning data"""
    try:
        print("\n=== Checking Data ===")
        response = requests.get(f"{RENDER_API_URL}/api/all")
        print(f"Data check: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return False
        
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

def main():
    """Main function"""
    print("=== Discord Export Fix Tool ===")
    print(f"Target API: {RENDER_API_URL}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check API health
    print("\n=== Step 1: Checking API Health ===")
    health_data = check_api_health()
    
    if not health_data:
        print("API health check failed")
        return
    
    # Step 2: Create and upload manual export files
    print("\n=== Step 2: Creating and Uploading Manual Export Files ===")
    if not create_manual_export_files():
        print("Failed to create and upload manual export files")
        return
    
    # Step 3: Check if data is available
    print("\n=== Step 3: Checking if Data is Available ===")
    max_attempts = 5
    wait_time = 5  # seconds
    
    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt}/{max_attempts} - Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        
        if check_data():
            print("Data is available!")
            break
    
    print("\n=== Export Fix Complete ===")
    print("If you're still having issues, please check the following:")
    print("1. Make sure the Discord bot is running properly")
    print("2. Make sure the Discord token is set correctly in the environment variables")
    print("3. Check the server logs for any errors")

if __name__ == "__main__":
    main()
