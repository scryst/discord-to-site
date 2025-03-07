import os
import json
import zipfile
import threading
import asyncio
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from src.config import EXPORT_DIR
from werkzeug.utils import secure_filename

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

    # Enable CORS for all routes, but restrict to specific domains in production
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://coffeechatventures.com"]}})
    
    # Start the Discord bot in a separate thread
    def start_discord_bot():
        global bot_started, bot_instance
        if not bot_started:
            bot_started = True
            try:
                from main import run_bot, bot
                bot_instance = bot
                bot_thread = threading.Thread(target=run_bot)
                bot_thread.daemon = True
                bot_thread.start()
                print("Discord bot started in a separate thread")
            except Exception as e:
                print(f"Error starting Discord bot: {e}")
    
    # Start the Discord bot when the app is created
    start_discord_bot()
    
    def get_latest_export():
        """Get the latest export summary file"""
        if not os.path.exists(EXPORT_DIR):
            return None
            
        summary_files = [f for f in os.listdir(EXPORT_DIR) if f.startswith('summary_') and f.endswith('.json')]
        
        if not summary_files:
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

    @app.route('/api/all')
    def api_all():
        """Return all data in a single response"""
        summary = get_latest_export()
        
        if not summary:
            return jsonify({"error": "No export data found", "status": "waiting_for_data"})
        
        try:
            result = {
                "summary": summary,
                "channels": load_data_file(summary['files']['channels']) if 'files' in summary and 'channels' in summary['files'] else [],
                "roles": load_data_file(summary['files']['roles']) if 'files' in summary and 'roles' in summary['files'] else [],
                "members": load_data_file(summary['files']['members']) if 'files' in summary and 'members' in summary['files'] else [],
                "events": load_data_file(summary['files']['events']) if 'files' in summary and 'events' in summary['files'] else []
            }
            
            return jsonify(result)
        except Exception as e:
            print(f"Error in api_all: {e}")
            return jsonify({"error": str(e), "status": "error"})

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

def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask web application"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_app(debug=True)
