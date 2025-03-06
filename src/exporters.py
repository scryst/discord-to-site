import os
import json
from datetime import datetime
from src.config import EXPORT_DIR

# Ensure export directory exists
os.makedirs(EXPORT_DIR, exist_ok=True)

def get_timestamp():
    """Generate a timestamp string for file naming"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

async def export_channels(guild, timestamp=None):
    """Export all channels to JSON"""
    if timestamp is None:
        timestamp = get_timestamp()
    
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
    
    # Save to file
    filepath = os.path.join(EXPORT_DIR, f'channels_{timestamp}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(channels_data, f, indent=4)
    
    return filepath

async def export_roles(guild, timestamp=None):
    """Export all roles to JSON"""
    if timestamp is None:
        timestamp = get_timestamp()
    
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
                'permissions': str(role.permissions),
                'mentionable': role.mentionable,
                'hoist': role.hoist,  # Whether the role is displayed separately in the member list
            }
            
            roles_data.append(role_info)
        except Exception as e:
            print(f"Error processing role {getattr(role, 'name', 'unknown')}: {e}")
    
    # Save to file
    filepath = os.path.join(EXPORT_DIR, f'roles_{timestamp}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(roles_data, f, indent=4)
    
    return filepath

async def export_members(guild, timestamp=None):
    """Export all members to JSON"""
    if timestamp is None:
        timestamp = get_timestamp()
    
    members_data = []
    
    try:
        # Try to get member count first
        print(f"Attempting to export {guild.member_count} members from {guild.name}")
        
        for member in guild.members:
            try:
                member_info = {
                    'id': member.id,
                    'name': member.name,
                    'display_name': member.display_name,
                    'joined_at': member.joined_at.isoformat() if member.joined_at else None,
                    'bot': member.bot,
                    'roles': [{'id': role.id, 'name': role.name} for role in member.roles if role.name != '@everyone'],
                }
                
                # Status is not always available due to intents restrictions
                if hasattr(member, 'status'):
                    member_info['status'] = str(member.status)
                
                members_data.append(member_info)
            except Exception as e:
                print(f"Error processing member {getattr(member, 'name', 'unknown')}: {e}")
    except Exception as e:
        print(f"Error accessing members list: {e}")
        print("This is likely due to missing privileged intents. Please enable SERVER MEMBERS INTENT in the Discord Developer Portal.")
        
        # Add a placeholder entry to indicate the issue
        members_data = [{
            'error': 'Could not access member data. Please enable SERVER MEMBERS INTENT in the Discord Developer Portal.',
            'member_count': getattr(guild, 'member_count', 'unknown')
        }]
    
    # Save to file
    filepath = os.path.join(EXPORT_DIR, f'members_{timestamp}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(members_data, f, indent=4)
    
    return filepath

async def export_events(guild, timestamp=None):
    """Export all scheduled events to JSON"""
    if timestamp is None:
        timestamp = get_timestamp()
    
    events_data = []
    
    try:
        # Fetch all scheduled events
        scheduled_events = await guild.fetch_scheduled_events()
        
        for event in scheduled_events:
            try:
                event_info = {
                    'id': event.id,
                    'name': event.name,
                    'description': event.description,
                    'start_time': event.start_time.isoformat() if event.start_time else None,
                    'end_time': event.end_time.isoformat() if event.end_time else None,
                    'location': str(event.location),
                    'creator_id': event.creator_id,
                    'status': str(event.status),
                }
                
                events_data.append(event_info)
            except Exception as e:
                print(f"Error processing event {getattr(event, 'name', 'unknown')}: {e}")
    except Exception as e:
        print(f"Error fetching scheduled events: {e}")
        events_data = [{"error": str(e)}]
    
    # Save to file
    filepath = os.path.join(EXPORT_DIR, f'events_{timestamp}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(events_data, f, indent=4)
    
    return filepath

async def export_all(guild):
    """Export all server data to JSON files"""
    timestamp = get_timestamp()
    
    # Create a dictionary to store all file paths
    export_files = {}
    
    # Export channels
    export_files['channels'] = await export_channels(guild, timestamp)
    print(f"Channels exported to {export_files['channels']}")
    
    # Export roles
    export_files['roles'] = await export_roles(guild, timestamp)
    print(f"Roles exported to {export_files['roles']}")
    
    # Export members
    export_files['members'] = await export_members(guild, timestamp)
    print(f"Members exported to {export_files['members']}")
    
    # Export scheduled events
    export_files['events'] = await export_events(guild, timestamp)
    print(f"Events exported to {export_files['events']}")
    
    # Create a summary file
    summary = {
        'server_name': guild.name,
        'server_id': guild.id,
        'export_time': datetime.now().isoformat(),
        'files': export_files
    }
    
    summary_path = os.path.join(EXPORT_DIR, f'summary_{timestamp}.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=4)
    
    print(f"Summary exported to {summary_path}")
    return summary_path
