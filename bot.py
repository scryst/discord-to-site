import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents (permissions)
intents = discord.Intents.default()
intents.members = True  # Need this to access member information
intents.message_content = True  # Need this to read message content

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='server_info')
async def server_info(ctx):
    """Command to fetch and display server information"""
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
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='export_server_data')
@commands.has_permissions(administrator=True)  # Only admins can use this command
async def export_server_data(ctx):
    """Export comprehensive server data to JSON files"""
    guild = ctx.guild
    await ctx.send("Starting server data export. This may take a moment...")
    
    # Create directory for exports if it doesn't exist
    os.makedirs('server_data', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export channels
    await export_channels(guild, timestamp)
    
    # Export roles
    await export_roles(guild, timestamp)
    
    # Export members
    await export_members(guild, timestamp)
    
    # Export scheduled events
    await export_events(guild, timestamp)
    
    await ctx.send("Server data export complete! Check the `server_data` folder.")

async def export_channels(guild, timestamp):
    """Export all channels to JSON"""
    channels_data = []
    
    for channel in guild.channels:
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
    
    # Save to file
    with open(f'server_data/channels_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(channels_data, f, indent=4)

async def export_roles(guild, timestamp):
    """Export all roles to JSON"""
    roles_data = []
    
    for role in guild.roles:
        # Skip @everyone role
        if role.name == '@everyone':
            continue
            
        role_info = {
            'id': role.id,
            'name': role.name,
            'color': str(role.color),
            'position': role.position,
            'permissions': str(role.permissions),
            'mentionable': role.mentionable,
            'hoist': role.hoist,  # Whether the role is displayed separately in the member list
        }
        
        roles_data.append(role_info)
    
    # Save to file
    with open(f'server_data/roles_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(roles_data, f, indent=4)

async def export_members(guild, timestamp):
    """Export all members to JSON"""
    members_data = []
    
    for member in guild.members:
        member_info = {
            'id': member.id,
            'name': member.name,
            'display_name': member.display_name,
            'joined_at': member.joined_at.isoformat() if member.joined_at else None,
            'bot': member.bot,
            'roles': [{'id': role.id, 'name': role.name} for role in member.roles if role.name != '@everyone'],
            'status': str(member.status) if hasattr(member, 'status') else 'unknown',
        }
        
        members_data.append(member_info)
    
    # Save to file
    with open(f'server_data/members_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(members_data, f, indent=4)

async def export_events(guild, timestamp):
    """Export all scheduled events to JSON"""
    events_data = []
    
    # Fetch all scheduled events
    scheduled_events = await guild.fetch_scheduled_events()
    
    for event in scheduled_events:
        event_info = {
            'id': event.id,
            'name': event.name,
            'description': event.description,
            'start_time': event.start_time.isoformat() if event.start_time else None,
            'end_time': event.end_time.isoformat() if event.end_time else None,
            'location': event.location,
            'creator_id': event.creator_id,
            'status': str(event.status),
        }
        
        events_data.append(event_info)
    
    # Save to file
    with open(f'server_data/events_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(events_data, f, indent=4)

# Run the bot
if __name__ == "__main__":
    if not TOKEN:
        print("Error: No Discord token found. Please add DISCORD_TOKEN to your .env file.")
    else:
        bot.run(TOKEN)
