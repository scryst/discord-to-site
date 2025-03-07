import os
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.config import EXPORT_DIR

# Create export directory if it doesn't exist
os.makedirs(EXPORT_DIR, exist_ok=True)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

    # Enable CORS for all routes, but restrict to specific domains in production
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://coffeechatventures.com"]}})
    
    def get_latest_export():
        """Get the latest export summary file"""
        if not os.path.exists(EXPORT_DIR):
            return None
            
        summary_files = [f for f in os.listdir(EXPORT_DIR) if f.startswith('summary_') and f.endswith('.json')]
        
        if not summary_files:
            return None
        
        # Sort by timestamp (which is part of the filename)
        latest_summary = sorted(summary_files, reverse=True)[0]
        
        with open(os.path.join(EXPORT_DIR, latest_summary), 'r', encoding='utf-8') as f:
            return json.load(f)

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
        
        result = {
            "summary": summary,
            "channels": load_data_file(summary['files']['channels']) if 'files' in summary and 'channels' in summary['files'] else [],
            "roles": load_data_file(summary['files']['roles']) if 'files' in summary and 'roles' in summary['files'] else [],
            "members": load_data_file(summary['files']['members']) if 'files' in summary and 'members' in summary['files'] else [],
            "events": load_data_file(summary['files']['events']) if 'files' in summary and 'events' in summary['files'] else []
        }
        
        return jsonify(result)

    @app.route('/api/health')
    def api_health():
        """Health check endpoint"""
        return jsonify({"status": "ok", "version": "1.0.0"})
    
    return app

# Global app instance for running directly
app = create_app()

def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask web application"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_web_app(debug=True)
