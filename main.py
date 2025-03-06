import asyncio
import os
import discord
from discord.ext import commands
import threading
from src.config import DISCORD_TOKEN, COMMAND_PREFIX
from src.web_app import run_web_app

# Set up intents (permissions)
intents = discord.Intents.default()
intents.members = True  # Need this to access member information
intents.message_content = True  # Need this to read message content

# Create bot instance
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Serving {len(bot.guilds)} guilds')
    
    # Print guild information
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')
    
    # Load commands cog
    try:
        from src.commands import setup
        await setup(bot)
        print("Commands loaded successfully")
    except Exception as e:
        print(f"Error loading commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param}")
    elif isinstance(error, commands.errors.CommandNotFound):
        # Ignore command not found errors
        pass
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        print(f"Command error: {error}")
        await ctx.send(f"An error occurred: {error}")

def run_bot():
    """Run the Discord bot"""
    if not DISCORD_TOKEN:
        print("Error: No Discord token found. Please add DISCORD_TOKEN to your .env file.")
        return
    
    try:
        print("Starting Discord bot with token:", DISCORD_TOKEN[:10] + "...")
        asyncio.run(bot.start(DISCORD_TOKEN))
    except discord.errors.LoginFailure:
        print("Error: Invalid Discord token. Please check your .env file.")
    except discord.errors.PrivilegedIntentsRequired:
        print("Error: Privileged intents are required but not enabled for this bot.")
        print("Please enable the 'SERVER MEMBERS INTENT' and 'MESSAGE CONTENT INTENT' in the Discord Developer Portal.")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Select your application")
        print("3. Go to the 'Bot' tab")
        print("4. Enable the 'SERVER MEMBERS INTENT' and 'MESSAGE CONTENT INTENT' under 'Privileged Gateway Intents'")
    except KeyboardInterrupt:
        print("Bot shutdown requested")
    except Exception as e:
        print(f"Error running bot: {e}")

def run_website(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask website"""
    try:
        run_web_app(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"Error running website: {e}")

if __name__ == "__main__":
    # Create a thread for the web server
    web_thread = threading.Thread(target=run_website, kwargs={'debug': False, 'port': 5000})
    web_thread.daemon = True  # This ensures the thread will exit when the main program exits
    web_thread.start()
    
    print("Web server started on http://localhost:5000")
    print("Starting Discord bot...")
    
    # Run the bot in the main thread
    run_bot()
