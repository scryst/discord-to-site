# Discord Server to Website Exporter

This project allows you to export information from a Discord server (channels, roles, members, events) and display it on a web interface, with support for deployment to Vercel.

## Features

- Export Discord server data to JSON files
- Display server information on a web interface
- Real-time data visualization with charts
- Responsive design that works on all devices
- API endpoints for integration with Vercel or other frontends
- CORS support for cross-origin requests

## Requirements

- Python 3.8 or higher
- Discord Bot Token (with proper permissions)
- Discord server with administrator access

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
3. Edit the `.env` file and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_token_here
   ```

### 4. Run the Application

1. Start the bot and web server:
   ```
   python main.py
   ```
2. The web server will start on http://localhost:5000
3. The Discord bot will connect to Discord

## Usage

### Discord Commands

- `!server_info` - Display basic server information
- `!export` - Export comprehensive server data (admin only)

### Web Interface

The web interface displays the exported server data with the following sections:

- **Channels** - List of all channels with type and category
- **Roles** - List of all roles with member counts and properties
- **Members** - List of all members with roles and join dates
- **Events** - List of all scheduled events

## API Endpoints

The following API endpoints are available for integration with external applications:

- `/api/summary` - Get the latest export summary
- `/api/channels` - Get the latest channels data
- `/api/roles` - Get the latest roles data
- `/api/members` - Get the latest members data
- `/api/events` - Get the latest events data
- `/api/all` - Get all data in a single response
- `/api/health` - Health check endpoint

## Vercel Deployment

A Next.js frontend example is included in the `vercel-example` directory, ready to be deployed to Vercel:

1. Push the code to GitHub
2. Connect your GitHub repository to Vercel
3. Set the environment variable `NEXT_PUBLIC_API_URL` to your API URL
4. Deploy!

For detailed deployment instructions, see the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) file.

## Project Structure

- `main.py` - Main entry point that runs both the bot and web server
- `src/`
  - `config.py` - Configuration settings
  - `commands.py` - Discord bot commands
  - `exporters.py` - Functions to export server data
  - `web_app.py` - Flask web application
- `templates/` - HTML templates for the web interface
- `static/` - Static files (CSS, JS, images)
- `server_data/` - Exported server data (JSON files)
- `vercel-example/` - Next.js frontend for Vercel deployment

## Customization

You can customize the following aspects of the application:

- **Bot Command Prefix**: Edit the `COMMAND_PREFIX` variable in `src/config.py`
- **Web Interface**: Edit the HTML templates in the `templates/` directory
- **Export Format**: Modify the exporter functions in `src/exporters.py`
- **Vercel Frontend**: Customize the Next.js application in the `vercel-example/` directory

## Troubleshooting

- **Bot doesn't connect**: Make sure your token is correct in the `.env` file
- **Missing permissions**: Ensure the bot has the necessary permissions in your server
- **Web server issues**: Check if port 5000 is already in use on your system
- **CORS errors**: Check the CORS configuration in `src/web_app.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
