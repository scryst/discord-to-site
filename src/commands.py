import discord
from discord.ext import commands, tasks
from src.exporters import export_all
import datetime

class ServerInfoCommands(commands.Cog):
    """Commands for fetching and exporting server information"""
    
    def __init__(self, bot):
        self.bot = bot
        # Start the scheduled export task
        self.scheduled_export.start()
    
    def cog_unload(self):
        # Make sure to cancel the task when the cog is unloaded
        self.scheduled_export.cancel()
    
    @tasks.loop(hours=6)  # Run every 6 hours
    async def scheduled_export(self):
        """Automatically export server data on a schedule"""
        # Wait until the bot is ready before starting the task
        await self.bot.wait_until_ready()
        
        # Only run if the bot is in at least one guild
        if not self.bot.guilds:
            print("Scheduled export: No guilds available")
            return
            
        guild = self.bot.guilds[0]
        print(f"Scheduled export: Starting automatic export for {guild.name} at {datetime.datetime.now()}")
        
        try:
            # Export all server data
            summary_path = await export_all(guild)
            print(f"Scheduled export: Completed successfully. Summary file: {summary_path}")
        except Exception as e:
            print(f"Scheduled export: Error during export: {str(e)}")
    
    @scheduled_export.before_loop
    async def before_scheduled_export(self):
        """Wait until the bot is ready before starting the scheduled task"""
        await self.bot.wait_until_ready()
        print(f"Scheduled export: Task initialized, will run every 6 hours")
    
    @commands.command(name='server_info')
    async def server_info(self, ctx):
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
        
        # Add basic server stats - avoid pinging the owner
        embed.add_field(name="Owner", value=f"{guild.owner.name}#{guild.owner.discriminator}" if hasattr(guild.owner, "discriminator") else guild.owner.name, inline=True)
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
    
    @commands.command(name='export')
    @commands.has_permissions(administrator=True)  # Only admins can use this command
    async def export_server_data(self, ctx):
        """Export comprehensive server data to JSON files"""
        if hasattr(ctx, 'guild') and ctx.guild:
            guild = ctx.guild
            await ctx.send("Starting server data export. This may take a moment...")
            
            try:
                # Export all server data
                summary_path = await export_all(guild)
                
                await ctx.send(f"Server data export complete! Check the `server_data` folder.\nSummary file: `{summary_path}`")
            except Exception as e:
                await ctx.send(f"Error during export: {str(e)}")
        else:
            # This is likely an API call without a guild context
            # Get the first guild the bot is in
            if not hasattr(self, 'bot') or not self.bot or not self.bot.guilds:
                await ctx.send("No guilds available for export")
                return
                
            guild = self.bot.guilds[0]
            await ctx.send(f"Starting server data export for {guild.name}. This may take a moment...")
            
            try:
                # Export all server data
                summary_path = await export_all(guild)
                
                await ctx.send(f"Server data export complete! Check the `server_data` folder.\nSummary file: `{summary_path}`")
            except Exception as e:
                await ctx.send(f"Error during export: {str(e)}")
    
    @export_server_data.error
    async def export_server_data_error(self, ctx, error):
        """Error handler for the export command"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need administrator permissions to use this command.")
        else:
            await ctx.send(f"An error occurred: {str(error)}")

    @commands.command(name='schedule')
    @commands.has_permissions(administrator=True)  # Only admins can use this command
    async def schedule_command(self, ctx, action="status"):
        """Control the scheduled export (status, start, stop, interval)"""
        action = action.lower()
        
        if action == "status":
            status = "running" if self.scheduled_export.is_running() else "stopped"
            next_run = self.scheduled_export.next_iteration
            next_run_str = next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else "N/A"
            interval = f"{self.scheduled_export.hours} hours"
            
            embed = discord.Embed(
                title="Scheduled Export Status",
                description=f"The scheduled export task is currently **{status}**.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Interval", value=interval, inline=True)
            embed.add_field(name="Next Run", value=next_run_str, inline=True)
            
            await ctx.send(embed=embed)
            
        elif action == "start":
            if not self.scheduled_export.is_running():
                self.scheduled_export.start()
                await ctx.send("✅ Scheduled export task started.")
            else:
                await ctx.send("⚠️ Scheduled export task is already running.")
                
        elif action == "stop":
            if self.scheduled_export.is_running():
                self.scheduled_export.cancel()
                await ctx.send("🛑 Scheduled export task stopped.")
            else:
                await ctx.send("⚠️ Scheduled export task is already stopped.")
                
        elif action.startswith("interval:"):
            try:
                # Extract the hours from the command (e.g., "interval:12" sets it to 12 hours)
                hours = int(action.split(":")[1])
                if hours < 1:
                    await ctx.send("⚠️ Interval must be at least 1 hour.")
                    return
                    
                # Restart the task with the new interval
                was_running = self.scheduled_export.is_running()
                if was_running:
                    self.scheduled_export.cancel()
                    
                self.scheduled_export.change_interval(hours=hours)
                
                if was_running:
                    self.scheduled_export.start()
                    
                await ctx.send(f"⏱️ Scheduled export interval changed to {hours} hours.")
            except (IndexError, ValueError):
                await ctx.send("⚠️ Invalid interval format. Use `!schedule interval:6` to set a 6-hour interval.")
        else:
            await ctx.send("⚠️ Unknown action. Available actions: status, start, stop, interval:X")
    
    @schedule_command.error
    async def schedule_command_error(self, ctx, error):
        """Error handler for the schedule command"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need administrator permissions to use this command.")
        else:
            await ctx.send(f"An error occurred: {str(error)}")

# Standalone export function for API calls
async def export_server_data(ctx):
    """Export comprehensive server data to JSON files (standalone version)"""
    from main import bot
    
    if not bot or not bot.guilds:
        if hasattr(ctx, 'send'):
            await ctx.send("No guilds available for export")
        return None
    
    guild = bot.guilds[0]
    if hasattr(ctx, 'send'):
        await ctx.send(f"Starting server data export for {guild.name}. This may take a moment...")
    
    try:
        # Export all server data
        summary_path = await export_all(guild)
        
        if hasattr(ctx, 'send'):
            await ctx.send(f"Server data export complete! Check the `server_data` folder.\nSummary file: `{summary_path}`")
        
        return summary_path
    except Exception as e:
        if hasattr(ctx, 'send'):
            await ctx.send(f"Error during export: {str(e)}")
        return None

async def setup(bot):
    """Add the ServerInfoCommands cog to the bot"""
    await bot.add_cog(ServerInfoCommands(bot))
