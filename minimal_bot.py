import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents (permissions) - using only default intents
intents = discord.Intents.default()

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot ID: {bot.user.id}')
    print(f'Serving {len(bot.guilds)} guilds')
    
    # Print guild information
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id})')

@bot.command(name='hello')
async def hello(ctx):
    """Simple command to test if the bot is working"""
    await ctx.send(f'Hello {ctx.author.name}! I am up and running.')

@bot.command(name='server_info')
async def server_info(ctx):
    """Display basic server information"""
    guild = ctx.guild
    
    # Create an embed for nicer display
    embed = discord.Embed(
        title=f"{guild.name} Server Information",
        description=f"Server ID: {guild.id}",
        color=discord.Color.blue()
    )
    
    # Add server icon if available
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    # Add basic server stats
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    
    # Add channel counts
    text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
    voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
    categories = len([c for c in guild.channels if isinstance(c, discord.CategoryChannel)])
    
    embed.add_field(name="Text Channels", value=text_channels, inline=True)
    embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
    embed.add_field(name="Categories", value=categories, inline=True)
    
    # Add role count
    embed.add_field(name="Roles", value=len(guild.roles) - 1, inline=True)  # -1 to exclude @everyone
    
    await ctx.send(embed=embed)

@bot.command(name='export_basic')
async def export_basic(ctx):
    """Export basic server data to JSON files"""
    guild = ctx.guild
    await ctx.send("Starting basic server data export. This may take a moment...")
    
    # Create directory for exports if it doesn't exist
    os.makedirs('server_data', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export basic server info
    server_info = {
        'id': guild.id,
        'name': guild.name,
        'description': guild.description,
        'member_count': guild.member_count,
        'created_at': guild.created_at.isoformat(),
        'icon_url': str(guild.icon.url) if guild.icon else None,
    }
    
    # Export channels
    channels_data = []
    for channel in guild.channels:
        try:
            channel_info = {
                'id': channel.id,
                'name': channel.name,
                'type': str(channel.type),
                'position': channel.position,
            }
            
            # Add category information if applicable
            if hasattr(channel, 'category') and channel.category:
                channel_info['category'] = {
                    'id': channel.category.id,
                    'name': channel.category.name
                }
            
            channels_data.append(channel_info)
        except Exception as e:
            print(f"Error processing channel {getattr(channel, 'name', 'unknown')}: {e}")
    
    # Export roles
    roles_data = []
    for role in guild.roles:
        try:
            # Skip @everyone role
            if role.name == '@everyone':
                continue
                
            role_info = {
                'id': role.id,
                'name': role.name,
                'color': str(role.color),
                'position': role.position,
                'mentionable': role.mentionable,
                'hoist': role.hoist,  # Whether the role is displayed separately in the member list
            }
            
            roles_data.append(role_info)
        except Exception as e:
            print(f"Error processing role {getattr(role, 'name', 'unknown')}: {e}")
    
    # Combine all data
    export_data = {
        'server': server_info,
        'channels': channels_data,
        'roles': roles_data,
        'export_time': datetime.now().isoformat()
    }
    
    # Save to file
    filepath = os.path.join('server_data', f'basic_export_{timestamp}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=4)
    
    await ctx.send(f"Basic server data export complete! Check the `server_data/{os.path.basename(filepath)}` file.")

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please add DISCORD_TOKEN to your .env file.")
    else:
        print("Starting Discord bot with token:", TOKEN[:10] + "...")
        try:
            bot.run(TOKEN)
        except discord.errors.LoginFailure:
            print("Error: Invalid Discord token. Please check your .env file.")
        except Exception as e:
            print(f"Error running bot: {e}")
