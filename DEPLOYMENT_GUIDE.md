# Deployment Guide for Coffee Chat Ventures Discord Bot

This guide will help you deploy your Discord bot and connect it to your Vercel site at coffeechatventures.com.

## Part 1: Discord Bot Setup

1. **Enable Privileged Intents**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Select your application (ID: 1347343694646214688)
   - Go to the "Bot" tab
   - Under "Privileged Gateway Intents", enable:
     - SERVER MEMBERS INTENT
     - MESSAGE CONTENT INTENT
   - Save your changes

2. **Add Bot to Your Server**
   - Use this OAuth URL to add your bot to your server:
     ```
     https://discord.com/api/oauth2/authorize?client_id=1347343694646214688&permissions=2147601408&scope=bot%20applications.commands
     ```

3. **Run the Bot**
   - Make sure your `.env` file contains the correct token
   - Run the bot: `python main.py`
   - Use the `!export` command in your Discord server to generate server data

## Part 2: API Deployment

You have two options for deploying your Discord bot's API:

### Option 1: Deploy to a VPS or Cloud Service

1. **Set Up a VPS** (DigitalOcean, AWS, etc.)
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 "src.web_app:app"
   ```
4. **Set Up Nginx** (optional, for SSL and proxy)
5. **Configure Domain** to point to your server

### Option 2: Deploy to a Serverless Platform

1. **Modify for Serverless** (AWS Lambda, Vercel Serverless Functions, etc.)
2. **Deploy API Code**
3. **Configure Domain** for your API

## Part 3: Vercel Frontend Deployment

1. **Create a GitHub Repository** for your frontend code
2. **Push the Vercel Example Code**
   ```bash
   cd vercel-example
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```
3. **Connect to Vercel**
   - Go to [Vercel](https://vercel.com)
   - Import your GitHub repository
   - Set the environment variable:
     - `NEXT_PUBLIC_API_URL` = URL of your deployed API
   - Deploy

4. **Configure Domain**
   - In Vercel dashboard, go to "Domains"
   - Add your domain: coffeechatventures.com
   - Follow Vercel's instructions to configure DNS

## Part 4: CORS Configuration

Make sure your API allows requests from your Vercel site:

1. The Flask app is already configured with CORS for:
   - http://localhost:3000 (development)
   - https://coffeechatventures.com (production)

2. If you need to add more domains, update the CORS configuration in `src/web_app.py`:
   ```python
   CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://coffeechatventures.com", "YOUR_NEW_DOMAIN"]}})
   ```

## Part 5: Testing

1. **Test Discord Bot**
   - Invite the bot to your server
   - Run `!server_info` to check basic info
   - Run `!export` to generate server data

2. **Test API**
   - Access `http://YOUR_API_URL/api/health` to check if the API is running
   - Access `http://YOUR_API_URL/api/summary` to check if data is available

3. **Test Frontend**
   - Visit your Vercel site
   - Check if data is loading correctly
   - Test all tabs: Summary, Channels, Roles, Members, Events

## Troubleshooting

- **Discord Bot Not Connecting**: Check your token and enabled intents
- **API Not Working**: Check if the server is running and accessible
- **CORS Errors**: Make sure your API allows requests from your frontend domain
- **No Data Showing**: Run the `!export` command in Discord to generate data

## Maintenance

- Keep your bot running 24/7 using a process manager like PM2
- Set up automatic backups of your exported data
- Monitor your API and bot for errors

For any questions or issues, refer to the documentation or create an issue in your GitHub repository.
