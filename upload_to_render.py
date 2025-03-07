import os
import requests
import json
from pathlib import Path

# Configuration
RENDER_API_URL = "https://discord-to-site-api.onrender.com/api/upload"
SERVER_DATA_DIR = "server_data"
API_KEY = "your_api_key"  # You would need to implement this in your API

def upload_files():
    """Upload all JSON files from server_data directory to Render"""
    # Get all JSON files in the server_data directory
    json_files = list(Path(SERVER_DATA_DIR).glob("*.json"))
    
    if not json_files:
        print("No JSON files found in server_data directory")
        return
    
    print(f"Found {len(json_files)} JSON files to upload")
    
    # For each file, read its contents and upload to Render
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Create payload
            payload = {
                "filename": file_path.name,
                "data": file_data,
                "api_key": API_KEY
            }
            
            # Upload to Render
            print(f"Uploading {file_path.name}...")
            response = requests.post(RENDER_API_URL, json=payload)
            
            if response.status_code == 200:
                print(f"Successfully uploaded {file_path.name}")
            else:
                print(f"Failed to upload {file_path.name}: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error uploading {file_path.name}: {e}")
    
    print("Upload complete")

if __name__ == "__main__":
    upload_files()
