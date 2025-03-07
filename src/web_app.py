import os
import json
import zipfile
import threading
import asyncio
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from src.config import EXPORT_DIR
from werkzeug.utils import secure_filename
from datetime import datetime
from collections import Counter

# Create export directory if it doesn't exist
os.makedirs(EXPORT_DIR, exist_ok=True)

# Global variable to track if bot is already running
bot_started = False
bot_instance = None

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    # Enable CORS for all routes and all origins
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
    
    # Start the Discord bot in a separate thread
    def start_discord_bot():
        global bot_started, bot_instance
        if not bot_started:
            bot_started = True
            try:
                # Import here to avoid circular imports
                import importlib
                main_module = importlib.import_module('main')
                bot_instance = main_module.bot
                # Don't start the bot here, it's already started in main.py
                print("Discord bot instance connected from main module")
            except Exception as e:
                print(f"Error connecting to Discord bot: {e}")
    
    # Connect to the Discord bot when the app is created
    start_discord_bot()
    
    def get_latest_export():
        """Get the latest export summary file"""
        if not os.path.exists(EXPORT_DIR):
            print(f"Export directory does not exist: {EXPORT_DIR}")
            return None
            
        summary_files = [f for f in os.listdir(EXPORT_DIR) if f.startswith('summary_') and f.endswith('.json')]
        
        if not summary_files:
            print(f"No summary files found in {EXPORT_DIR}")
            # Try to find any JSON files and create a summary
            json_files = [f for f in os.listdir(EXPORT_DIR) if f.endswith('.json')]
            if json_files:
                print(f"Found {len(json_files)} JSON files in {EXPORT_DIR}")
                # Extract timestamp from filenames (assuming format like 'channels_20250307_102809.json')
                timestamps = []
                for filename in json_files:
                    parts = filename.split('_')
                    if len(parts) >= 3:
                        try:
                            timestamp = f"{parts[1]}_{parts[2].split('.')[0]}"
                            timestamps.append(timestamp)
                        except:
                            pass
                
                if timestamps:
                    most_common_timestamp = Counter(timestamps).most_common(1)[0][0]
                    print(f"Using timestamp: {most_common_timestamp}")
                    
                    # Create a summary file
                    summary = {
                        "server_name": "Coffee Chat Ventures",
                        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "files": {
                            "channels": os.path.join(EXPORT_DIR, f"channels_{most_common_timestamp}.json"),
                            "roles": os.path.join(EXPORT_DIR, f"roles_{most_common_timestamp}.json"),
                            "members": os.path.join(EXPORT_DIR, f"members_{most_common_timestamp}.json"),
                            "events": os.path.join(EXPORT_DIR, f"events_{most_common_timestamp}.json")
                        }
                    }
                    
                    # Save the summary file
                    summary_filename = f"summary_{most_common_timestamp}.json"
                    summary_path = os.path.join(EXPORT_DIR, summary_filename)
                    with open(summary_path, 'w', encoding='utf-8') as f:
                        json.dump(summary, f, indent=2)
                    
                    print(f"Created summary file: {summary_path}")
                    
                    # Return the newly created summary
                    return summary
            
            return None
        
        # Sort by timestamp (which is part of the filename)
        latest_summary = sorted(summary_files, reverse=True)[0]
        
        try:
            with open(os.path.join(EXPORT_DIR, latest_summary), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading summary file: {e}")
            return None

    def load_data_file(filepath):
        """Load data from a JSON file"""
        try:
            if not os.path.exists(filepath):
                return {"error": f"File not found: {filepath}"}
                
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            return {"error": str(e)}

    @app.route('/')
    def index():
        """Render the main page"""
        summary = get_latest_export()
        
        if not summary:
            return render_template('no_data.html')
        
        return render_template('index.html', server_name=summary['server_name'])

    @app.route('/api/summary')
    def api_summary():
        """Return the latest export summary"""
        summary = get_latest_export()
        
        if not summary:
            return jsonify({"error": "No export data found", "status": "waiting_for_data"})
        
        return jsonify(summary)

    @app.route('/api/channels')
    def api_channels():
        """Return the latest channels data"""
        summary = get_latest_export()
        
        if not summary or 'files' not in summary or 'channels' not in summary['files']:
            return jsonify({"error": "No channels data found", "status": "waiting_for_data"})
        
        channels_data = load_data_file(summary['files']['channels'])
        return jsonify(channels_data)

    @app.route('/api/roles')
    def api_roles():
        """Return the latest roles data"""
        summary = get_latest_export()
        
        if not summary or 'files' not in summary or 'roles' not in summary['files']:
            return jsonify({"error": "No roles data found", "status": "waiting_for_data"})
        
        roles_data = load_data_file(summary['files']['roles'])
        return jsonify(roles_data)

    @app.route('/api/members')
    def api_members():
        """Return the latest members data"""
        summary = get_latest_export()
        
        if not summary or 'files' not in summary or 'members' not in summary['files']:
            return jsonify({"error": "No members data found", "status": "waiting_for_data"})
        
        members_data = load_data_file(summary['files']['members'])
        return jsonify(members_data)

    @app.route('/api/events')
    def api_events():
        """Return the latest events data"""
        summary = get_latest_export()
        
        if not summary or 'files' not in summary or 'events' not in summary['files']:
            return jsonify({"error": "No events data found", "status": "waiting_for_data"})
        
        events_data = load_data_file(summary['files']['events'])
        return jsonify(events_data)

    @app.route('/api/all', methods=['GET', 'OPTIONS'])
    def api_all():
        """Return all data in a single response"""
        # Handle OPTIONS request for CORS preflight
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'GET')
            return response
            
        summary = get_latest_export()
        
        if not summary:
            error_response = jsonify({"error": "No export data found", "status": "waiting_for_data"})
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            error_response.headers.add('Access-Control-Allow-Methods', 'GET')
            return error_response
        
        try:
            result = {
                "summary": summary,
                "channels": load_data_file(summary['files']['channels']) if 'files' in summary and 'channels' in summary['files'] else [],
                "roles": load_data_file(summary['files']['roles']) if 'files' in summary and 'roles' in summary['files'] else [],
                "members": load_data_file(summary['files']['members']) if 'files' in summary and 'members' in summary['files'] else [],
                "events": load_data_file(summary['files']['events']) if 'files' in summary and 'events' in summary['files'] else []
            }
            
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'GET')
            return response
        except Exception as e:
            print(f"Error in api_all: {e}")
            error_response = jsonify({"error": str(e), "status": "error"})
            error_response.headers.add('Access-Control-Allow-Origin', '*')
            error_response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            error_response.headers.add('Access-Control-Allow-Methods', 'GET')
            return error_response

    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        return jsonify({
            "status": "ok", 
            "version": "1.0.0",
            "bot_running": bot_started,
            "export_dir_exists": os.path.exists(EXPORT_DIR),
            "export_files": os.listdir(EXPORT_DIR) if os.path.exists(EXPORT_DIR) else []
        })

    @app.route('/api/realtime')
    def api_realtime():
        """Return real-time data about online members and active channels"""
        global bot_instance
        
        if not bot_instance or not bot_instance.guilds:
            return jsonify({"error": "Bot not connected", "status": "offline"})
            
        guild = bot_instance.guilds[0]
        
        try:
            # Get online members
            online_members = []
            for member in guild.members:
                if hasattr(member, 'status') and str(member.status) != 'offline':
                    online_members.append({
                        'id': member.id,
                        'name': member.name,
                        'display_name': member.display_name,
                        'avatar_url': str(member.display_avatar.url) if hasattr(member, 'display_avatar') else None,
                        'status': str(member.status) if hasattr(member, 'status') else 'unknown'
                    })
            
            # Get active channels (channels with recent messages)
            active_channels = []
            for channel in guild.text_channels:
                try:
                    # Try to get the last message timestamp
                    last_message = None
                    async def get_last_message():
                        nonlocal last_message
                        messages = [msg async for msg in channel.history(limit=1)]
                        if messages:
                            last_message = messages[0]
                    
                    # Create a new event loop for the async call
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(get_last_message())
                    loop.close()
                    
                    if last_message:
                        active_channels.append({
                            'id': channel.id,
                            'name': channel.name,
                            'last_message_time': last_message.created_at.isoformat(),
                            'category': channel.category.name if channel.category else None
                        })
                except Exception as e:
                    print(f"Error getting last message for channel {channel.name}: {e}")
            
            # Sort active channels by last message time (most recent first)
            active_channels.sort(key=lambda x: x.get('last_message_time', ''), reverse=True)
            
            # Get voice channels with members
            active_voice_channels = []
            for channel in guild.voice_channels:
                if len(channel.members) > 0:
                    active_voice_channels.append({
                        'id': channel.id,
                        'name': channel.name,
                        'member_count': len(channel.members),
                        'members': [{'id': m.id, 'name': m.display_name} for m in channel.members]
                    })
            
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'guild_name': guild.name,
                'guild_id': guild.id,
                'total_members': guild.member_count,
                'online_members': online_members,
                'active_text_channels': active_channels,
                'active_voice_channels': active_voice_channels
            })
            
        except Exception as e:
            print(f"Error getting real-time data: {e}")
            return jsonify({"error": str(e), "status": "error"})

    @app.route('/api/cors', methods=['GET', 'OPTIONS'])
    def handle_cors():
        """Handle CORS preflight requests"""
        if request.method == 'OPTIONS':
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        return jsonify({"cors": "enabled"})

    @app.route('/api/create_directory', methods=['POST'])
    def api_create_directory():
        """Create the server_data directory if it doesn't exist"""
        try:
            os.makedirs(EXPORT_DIR, exist_ok=True)
            return jsonify({"status": "success", "message": f"Directory {EXPORT_DIR} created or already exists"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/api/upload_data', methods=['POST'])
    def api_upload_data():
        """Upload server data as a zip file"""
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        if file:
            try:
                # Save the zip file temporarily
                zip_path = os.path.join(os.path.dirname(EXPORT_DIR), 'temp.zip')
                file.save(zip_path)
                
                # Extract the zip file to the server_data directory
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(EXPORT_DIR))
                
                # Remove the temporary zip file
                os.remove(zip_path)
                
                return jsonify({
                    "status": "success", 
                    "message": "Data uploaded and extracted successfully",
                    "files": os.listdir(EXPORT_DIR)
                })
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/api/upload_file', methods=['POST'])
    def api_upload_file():
        """Upload a single file to the server_data directory"""
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400
        
        if file:
            try:
                # Ensure the directory exists
                os.makedirs(EXPORT_DIR, exist_ok=True)
                
                # Save the file to the server_data directory
                file_path = os.path.join(EXPORT_DIR, secure_filename(file.filename))
                file.save(file_path)
                
                print(f"Saved file to {file_path}")
                
                return jsonify({
                    "status": "success", 
                    "message": f"File {file.filename} uploaded successfully",
                    "path": file_path
                })
            except Exception as e:
                print(f"Error uploading file: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/api/trigger_export', methods=['POST'])
    def api_trigger_export():
        """Trigger a Discord data export"""
        try:
            # Import here to avoid circular imports
            import importlib
            commands_module = importlib.import_module('src.commands')
            
            # Create a dummy context
            class DummyContext:
                async def send(self, message):
                    print(f"API Export: {message}")
            
            # Create a background thread to run the export
            def run_export():
                asyncio.run(commands_module.export_server_data(DummyContext()))
            
            export_thread = threading.Thread(target=run_export)
            export_thread.daemon = True
            export_thread.start()
            
            return jsonify({
                "status": "success",
                "message": "Export triggered successfully in background thread"
            })
        except Exception as e:
            print(f"Error triggering export: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return app

# Global app instance for running directly
app = create_app()

# Function to run the Flask web application
def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask web application"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_app(debug=True)
