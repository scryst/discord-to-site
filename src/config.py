import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = '!'

# Export configuration
EXPORT_DIR = 'server_data'
