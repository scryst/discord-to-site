# Discord to Vercel Integration Guide

This guide explains how to set up your Discord bot on Render.com and integrate real-time Discord data with your Vercel site built with v0.dev.

## Architecture Overview

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│             │      │             │      │             │
│  Discord    │──────▶  Render.com │──────▶  Vercel     │
│  Server     │      │  API        │      │  Website    │
│             │      │             │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
```

- **Discord Server**: Source of data (members, channels, etc.)
- **Render.com**: Hosts your Discord bot and API
- **Vercel**: Hosts your website with v0.dev components

## Step 1: Deploy to Render.com

1. Create a new Render.com account if you don't have one: https://render.com
2. Connect your GitHub repository
3. Create a new Web Service
4. Select your repository
5. Configure the service:
   - **Name**: `discord-to-site` (or your preferred name)
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 1 'src.web_app:app'`
6. Add environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `PORT`: 5000

## Step 2: Set Up Automatic Updates

To keep your Vercel site updated with real-time Discord data:

1. In your Render.com dashboard, go to your web service
2. Navigate to "Events" and create a new Cron Job
3. Set it to run every 5-15 minutes with the command: `curl -X POST https://your-render-service.onrender.com/api/export`
4. This will periodically trigger your bot to export fresh Discord data

## Step 3: Integrate with Vercel

1. In your Vercel project, add an environment variable:
   - `NEXT_PUBLIC_API_URL`: The URL of your Render.com service (e.g., `https://discord-to-site.onrender.com`)

2. Import the Discord widget component in your v0.dev site:
   ```jsx
   import DiscordWidget from './components/DiscordWidget';
   
   // Then in your JSX:
   <DiscordWidget />
   ```

3. The widget will automatically fetch and display:
   - Online members
   - Active text channels
   - Voice channels with users
   - Real-time status updates

## Customization

You can customize the Discord widget by modifying the `DiscordWidget.jsx` file:

- Change the colors to match your site's theme
- Adjust the update interval (default is 60 seconds)
- Modify which data is displayed
- Add additional features like server stats

## Troubleshooting

- **CORS Issues**: Ensure your Render.com service has CORS properly configured
- **API Connection Errors**: Check that your environment variables are set correctly
- **Missing Data**: Verify your Discord bot has the necessary permissions

## Need Help?

If you encounter any issues, check the logs in your Render.com dashboard or open an issue in the GitHub repository.
