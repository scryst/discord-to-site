# Discord Server to Website Exporter

This project allows you to export information from a Discord server (channels, roles, members, events) and display it on a web interface, with support for deployment to Render and integration with Vercel sites.

## Features

- Export Discord server data to JSON files
- Display server information on a web interface
- Real-time data about online members and active channels
- API endpoints for accessing Discord server data
- Automated export functionality via API
- Scheduled exports every 6 hours (configurable)
- CORS support for cross-origin requests
- Robust error handling and logging
- Deployment support for Render
- Integration with Vercel sites (including v0.dev)

## Requirements

- Python 3.8 or higher
- Discord Bot Token (with proper permissions)
- Discord server with administrator access
- Render account (for deployment)

## Setup Instructions

### 1. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable:
   - Server Members Intent
   - Message Content Intent
5. Copy the bot token (you'll need this later)

### 2. Invite the Bot to Your Server

1. Go to the "OAuth2" > "URL Generator" tab
2. Select the following scopes:
   - `bot`
   - `applications.commands`
3. Select the following bot permissions:
   - View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Use Application Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 3. Install the Application

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_token_here
   ```

### 4. Run the Application Locally

1. Start the bot and web server:
   ```
   python main.py
   ```
2. The web server will start on http://localhost:5000
3. The Discord bot will connect to Discord

### 5. Deploy to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. Add the environment variable:
   - `DISCORD_TOKEN=your_discord_token_here`
5. Set the Health Check Path to: `/api/health`
6. Deploy the service

### 6. Integrate with Vercel

1. In your Vercel project, add an environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com`
2. Use the provided React component in the `vercel-integration` directory
3. The component will automatically fetch and display Discord data
4. For v0.dev sites, you can use the fetch code in your page.tsx/jsx files

## Usage

### Discord Commands

- `!server_info` - Display basic server information
- `!export` - Export comprehensive server data (admin only)
- `!schedule` - Control the scheduled export task (admin only)
  - `!schedule status` - Check the status of scheduled exports
  - `!schedule start` - Start the scheduled export task
  - `!schedule stop` - Stop the scheduled export task
  - `!schedule interval:X` - Change the interval to X hours (e.g., `!schedule interval:12`)

### API Endpoints

The following API endpoints are available for integration with external applications:

- `/api/summary` - Get the latest export summary
- `/api/channels` - Get the latest channels data
- `/api/roles` - Get the latest roles data
- `/api/members` - Get the latest members data
- `/api/events` - Get the latest events data
- `/api/all` - Get all data in a single response
- `/api/realtime` - Get real-time data about online members and active channels
- `/api/health` - Health check endpoint
- `/api/trigger_export` - Trigger a new export (POST request)
- `/api/create_directory` - Create the server_data directory if it doesn't exist
- `/api/upload_file` - Upload a file to the server_data directory

## Project Structure

- `main.py` - Main entry point that runs both the bot and web server
- `src/`
  - `config.py` - Configuration settings
  - `commands.py` - Discord bot commands
  - `exporters.py` - Functions to export server data
  - `web_app.py` - Flask web application
- `server_data/` - Exported server data (JSON files)
- `vercel-integration/` - Components and examples for Vercel integration
- `debug_export.py` - Script to debug export functionality
- `fix_render_export.py` - Script to fix export issues on Render
- `fix_render_paths.py` - Script to fix file paths on Render

## Utility Scripts

### debug_export.py

This script helps diagnose issues with the export functionality:
- Checks API health
- Triggers an export
- Verifies if data is available

### fix_render_export.py

This script helps fix export issues on Render:
- Creates export files manually using local data
- Uploads files to Render
- Checks if data is available through the API

### fix_render_paths.py

This script fixes file path issues on Render:
- Creates export files with Linux-style paths
- Uploads files to Render
- Checks if data is available through the API

## Troubleshooting

### Common Issues

- **Bot doesn't connect**: Make sure your token is correct in the environment variables
- **Missing permissions**: Ensure the bot has the necessary permissions in your server
- **No export data found**: Check if the server_data directory exists and has proper permissions
- **File path issues**: Make sure file paths use forward slashes (/) on Render
- **CORS errors**: The API is configured to allow all origins, but if you're still having issues, check browser console for specific errors
- **"Failed to fetch" in Vercel**: Ensure your Render service is running and the NEXT_PUBLIC_API_URL is correct

### Debugging Steps

1. Check API health:
   ```
   curl https://your-render-service.onrender.com/api/health
   ```

2. Test CORS configuration:
   ```
   curl -H "Origin: https://your-vercel-site.vercel.app" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS https://your-render-service.onrender.com/api/all
   ```

3. Fix export issues:
   ```
   python fix_render_export.py
   ```

4. Fix file path issues:
   ```
   python fix_render_paths.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
