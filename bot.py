"""
Main bot entry point
Initializes the Discord bot and loads all cogs
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
import sys
from datetime import datetime

import config
from database.db_manager import DatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('discord_bot')

class DiscordBot(commands.Bot):
    """Custom bot class with additional functionality"""
    
    def __init__(self):
        # Define intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True  # Required for member join/leave logging
        intents.moderation = True  # Required for ban/unban logging
        # Note: Enable these intents in Discord Developer Portal
        # intents.presences = True  # Optional
        
        # Initialize bot
        super().__init__(
            command_prefix=config.PREFIX,
            intents=intents,
            description=config.BOT_DESCRIPTION,
            help_command=None  # We'll create a custom help command
        )
        
        self.start_time = datetime.utcnow()
        self.db = None
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Starting bot setup...")
        
        # Initialize database
        self.db = DatabaseManager(config.DATABASE_PATH)
        await self.db.initialize()
        logger.info("Database initialized")
        
        # Load all cogs
        await self.load_cogs()
        
        # Sync commands with Discord
        logger.info("Syncing commands with Discord...")
        await self.tree.sync()
        logger.info("Commands synced")
    
    async def load_cogs(self):
        """Load all cog modules"""
        cogs_dir = 'cogs'
        
        # List of cog files to load
        # Note: Discord limits bots to 100 slash commands total
        cog_files = [
            'admin',  # Admin commands (shutdown, restart)
            'moderation',
            'automod',
            'kcl_antivirus_simple',  # KCLAntivirus system (simplified)
            'logging',
            # 'bloxfruits',  # Disabled - no reliable API
            # 'youtube',  # Removed - YouTube functionality disabled
            'economy',
            # 'music',  # Removed - Music/audio functionality disabled
            'utility',
            'fun',
            'custom_commands',
            'events',
            'giveaway',  # Giveaway system
            # Disabled to stay under 100 command limit:
            # 'advanced_moderation',
            # 'channel_management',
            # 'role_management',
            # 'server_management',
            # 'member_management',
            # 'extra_fun',
            # 'moderation_utilities'
        ]
        
        for cog_file in cog_files:
            try:
                await self.load_extension(f'{cogs_dir}.{cog_file}')
                logger.info(f"Loaded cog: {cog_file}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog_file}: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Bot is ready!")
        logger.info(f"Logged in as: {self.user.name} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Serving {sum(g.member_count for g in self.guilds)} users")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="/help")
        )
        
        # Send startup message to bot log channels
        await self.send_bot_log_to_all_guilds(
            title="🟢 Bot Started",
            description=f"**{self.user.name}** is now online and ready!",
            color=config.Colors.SUCCESS,
            fields=[
                ("Guilds", str(len(self.guilds)), True),
                ("Users", str(sum(g.member_count for g in self.guilds)), True),
                ("Latency", f"{round(self.latency * 1000)}ms", True)
            ]
        )
    
    async def send_bot_log_to_all_guilds(self, title: str, description: str, color: int, fields: list = None):
        """Send a log message to all guilds with bot logging enabled"""
        for guild in self.guilds:
            try:
                settings = await self.db.get_guild_settings(guild.id)
                if not settings.bot_log_channel:
                    continue
                
                channel = guild.get_channel(settings.bot_log_channel)
                if not channel:
                    continue
                
                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=color,
                    timestamp=datetime.utcnow()
                )
                
                if fields:
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                
                await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Failed to send bot log to guild {guild.id}: {e}")
    
    async def on_message(self, message):
        """Central message handler - processes all message events"""
        if message.author.bot:
            return
        
        # Debug logging
        logger.info(f"Message received: '{message.content}' from {message.author} in {message.guild}")
        
        # Check if it's a command
        if message.content.startswith(config.PREFIX):
            logger.info(f"Command detected with prefix '{config.PREFIX}': {message.content}")
        
        # Process commands at the end (this handles prefix commands)
        await self.process_commands(message)
    
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild"""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Update presence
        await self.change_presence(
            activity=discord.Game(name="Playing /help")
        )
        
        # Log to other guilds
        await self.send_bot_log_to_all_guilds(
            title="➕ Joined New Server",
            description=f"Bot joined **{guild.name}**",
            color=config.Colors.SUCCESS,
            fields=[
                ("Server ID", str(guild.id), True),
                ("Members", str(guild.member_count), True),
                ("Total Servers", str(len(self.guilds)), True)
            ]
        )
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild"""
        logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")
        
        # Update presence
        await self.change_presence(
            activity=discord.Game(name="/help")
        )
        
        # Log to remaining guilds
        await self.send_bot_log_to_all_guilds(
            title="➖ Left Server",
            description=f"Bot left **{guild.name}**",
            color=config.Colors.WARNING,
            fields=[
                ("Server ID", str(guild.id), True),
                ("Total Servers", str(len(self.guilds)), True)
            ]
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler for text commands"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"❌ You don't have permission to use this command.")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
            return
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ This command is on cooldown. Try again in {error.retry_after:.1f}s")
            return
        
        logger.error(f"Command error: {error}", exc_info=error)
        await ctx.send("❌ An error occurred while executing the command.")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Global error handler for slash commands"""
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ You don't have permission to use this command.",
                ephemeral=True
            )
            return
        
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏳ This command is on cooldown. Try again in {error.retry_after:.1f}s",
                ephemeral=True
            )
            return
        
        if isinstance(error, discord.app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ You don't meet the requirements to use this command.",
                ephemeral=True
            )
            return
        
        logger.error(f"App command error: {error}", exc_info=error)
        
        # Try to send error message
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ An error occurred while executing the command.",
                    ephemeral=True
                )
        except:
            pass
    
    async def close(self):
        """Cleanup when bot is shutting down"""
        logger.info("Shutting down bot...")
        
        # Send shutdown message to bot log channels (only if logged in)
        if self.user:
            await self.send_bot_log_to_all_guilds(
                title="🔴 Bot Shutting Down",
                description=f"**{self.user.name}** is going offline.",
                color=config.Colors.ERROR,
                fields=[
                    ("Uptime", f"<t:{int(self.start_time.timestamp())}:R>", True)
                ]
            )
        
        if self.db:
            await self.db.close()
        
        await super().close()

async def main():
    """Main function to run the bot"""
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Create and run bot
    bot = DiscordBot()
    
    try:
        await bot.start(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=e)
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
