import os
import requests
import json
import shutil
from pathlib import Path

# Configuration
RENDER_API_URL = "https://discord-to-site-api.onrender.com"
SERVER_DATA_DIR = "server_data"

def create_server_data_directory():
    """Create a server_data directory on Render by making an API call"""
    try:
        response = requests.post(f"{RENDER_API_URL}/api/create_directory")
        print(f"Create directory response: {response.status_code} - {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False

def upload_files():
    """Upload all JSON files from server_data directory to Render"""
    # Get all JSON files in the server_data directory
    json_files = list(Path(SERVER_DATA_DIR).glob("*.json"))
    
    if not json_files:
        print("No JSON files found in server_data directory")
        return
    
    print(f"Found {len(json_files)} JSON files to upload")
    
    # Create a temporary zip file of the server_data directory
    zip_path = "server_data.zip"
    shutil.make_archive("server_data", 'zip', SERVER_DATA_DIR)
    
    print(f"Created zip file at {zip_path}")
    
    # Upload the zip file to Render
    try:
        with open(zip_path, 'rb') as zip_file:
            files = {'file': zip_file}
            response = requests.post(f"{RENDER_API_URL}/api/upload_data", files=files)
            
        if response.status_code == 200:
            print(f"Successfully uploaded data: {response.text}")
        else:
            print(f"Failed to upload data: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error uploading data: {e}")
    
    # Clean up the temporary zip file
    try:
        os.remove(zip_path)
        print(f"Removed temporary zip file {zip_path}")
    except Exception as e:
        print(f"Error removing zip file: {e}")

if __name__ == "__main__":
    print("Starting data upload to Render...")
    create_server_data_directory()
    upload_files()
    print("Upload process completed")
