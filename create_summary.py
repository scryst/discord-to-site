import requests
import json
import os
from datetime import datetime

# Configuration
RENDER_API_URL = "https://discord-to-site-api.onrender.com"
SERVER_DATA_DIR = "server_data"

def create_summary_file():
    """Create a summary file that points to the existing data files"""
    # Get the latest timestamp from the existing files
    json_files = [f for f in os.listdir(SERVER_DATA_DIR) if f.endswith('.json')]
    if not json_files:
        print("No JSON files found in server_data directory")
        return
    
    # Extract timestamp from filenames (assuming format like 'summary_20250307_102809.json')
    timestamps = []
    for filename in json_files:
        parts = filename.split('_')
        if len(parts) >= 3:
            try:
                timestamp = f"{parts[1]}_{parts[2].split('.')[0]}"
                timestamps.append(timestamp)
            except:
                pass
    
    if not timestamps:
        print("Could not extract timestamps from filenames")
        return
    
    # Use the most common timestamp
    from collections import Counter
    most_common_timestamp = Counter(timestamps).most_common(1)[0][0]
    print(f"Using timestamp: {most_common_timestamp}")
    
    # Create a summary file
    summary = {
        "server_name": "Coffee Chat Ventures",
        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": {
            "channels": f"server_data/channels_{most_common_timestamp}.json",
            "roles": f"server_data/roles_{most_common_timestamp}.json",
            "members": f"server_data/members_{most_common_timestamp}.json",
            "events": f"server_data/events_{most_common_timestamp}.json"
        }
    }
    
    # Save the summary file locally
    summary_filename = f"summary_{most_common_timestamp}.json"
    summary_path = os.path.join(SERVER_DATA_DIR, summary_filename)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Created summary file: {summary_path}")
    
    # Trigger the export on Render to create the files
    try:
        response = requests.post(f"{RENDER_API_URL}/api/trigger_export")
        print(f"Trigger export response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error triggering export: {e}")

if __name__ == "__main__":
    print("Creating summary file...")
    create_summary_file()
    print("Done!")
