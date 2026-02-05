"""
Auto-moderation cog
Handles automatic moderation features like spam detection, word filtering, etc.
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import re

from utils.embeds import success_embed, warning_embed
from utils.checks import is_moderator
import config

class AutoMod(commands.Cog):
    """Auto-moderation features"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(list)  # user_id: [(timestamp, message_id), ...]
        self.invite_pattern = re.compile(r'discord(?:\.gg|app\.com/invite)/[a-zA-Z0-9]+')
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check messages for auto-mod violations"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Ignore moderators
        if message.author.guild_permissions.manage_messages:
            return
        
        # Get guild settings
        settings = await self.bot.db.get_guild_settings(message.guild.id)
        
        if not settings.automod_enabled:
            return
        
        # Check spam
        if settings.spam_detection:
            if await self._check_spam(message):
                return
        
        # Check blacklist
        if settings.blacklist_enabled:
            if await self._check_blacklist(message):
                return
        
        # Check caps
        if await self._check_caps(message):
            return
        
        # Check invite links
        if await self._check_invites(message):
            return
        
        # Check mass mentions
        if await self._check_mass_mentions(message):
            return
        
        # Check @everyone/@here pings
        if await self._check_everyone_pings(message):
            return
    
    async def _check_spam(self, message: discord.Message) -> bool:
        """Check for spam (multiple messages in short time)"""
        user_id = message.author.id
        now = datetime.utcnow()
        
        # Add current message to cache
        self.message_cache[user_id].append((now, message.id))
        
        # Remove old messages (older than time window)
        cutoff = now - timedelta(seconds=config.AutoMod.SPAM_TIME_WINDOW)
        self.message_cache[user_id] = [
            (ts, mid) for ts, mid in self.message_cache[user_id]
            if ts > cutoff
        ]
        
        # Check if spam threshold exceeded
        if len(self.message_cache[user_id]) >= config.AutoMod.SPAM_MESSAGE_COUNT:
            try:
                # Delete messages
                for _, msg_id in self.message_cache[user_id]:
                    try:
                        msg = await message.channel.fetch_message(msg_id)
                        await msg.delete()
                    except:
                        pass
                
                # Timeout user for 5 minutes
                await message.author.timeout(
                    timedelta(minutes=5),
                    reason="Auto-mod: Spam detected"
                )
                
                # Send warning
                embed = warning_embed(
                    "Spam Detected",
                    f"{message.author.mention} has been timed out for 5 minutes for spam."
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                # Clear cache
                self.message_cache[user_id].clear()
                
                return True
            except:
                pass
        
        return False
    
    async def _check_blacklist(self, message: discord.Message) -> bool:
        """Check for blacklisted words"""
        blacklist = await self.bot.db.get_blacklist(message.guild.id)
        
        if not blacklist:
            return False
        
        content_lower = message.content.lower()
        
        for word in blacklist:
            if word in content_lower:
                try:
                    await message.delete()
                    
                    # Warn user
                    await self.bot.db.add_warning(
                        message.author.id,
                        message.guild.id,
                        self.bot.user.id,
                        f"Auto-mod: Used blacklisted word '{word}'"
                    )
                    
                    embed = warning_embed(
                        "Blacklisted Word",
                        f"{message.author.mention}, your message contained a blacklisted word and has been deleted."
                    )
                    await message.channel.send(embed=embed, delete_after=5)
                    
                    return True
                except:
                    pass
        
        return False
    
    async def _check_caps(self, message: discord.Message) -> bool:
        """Check for excessive caps"""
        if len(message.content) < 10:
            return False
        
        caps_count = sum(1 for c in message.content if c.isupper())
        total_letters = sum(1 for c in message.content if c.isalpha())
        
        if total_letters == 0:
            return False
        
        caps_ratio = caps_count / total_letters
        
        if caps_ratio > config.AutoMod.CAPS_THRESHOLD:
            try:
                await message.delete()
                
                embed = warning_embed(
                    "Excessive Caps",
                    f"{message.author.mention}, please don't use excessive caps."
                )
                await message.channel.send(embed=embed, delete_after=5)
                
                return True
            except:
                pass
        
        return False
    
    async def _check_invites(self, message: discord.Message) -> bool:
        """Check for Discord invite links"""
        if self.invite_pattern.search(message.content):
            try:
                await message.delete()
                
                embed = warning_embed(
                    "Invite Link Blocked",
                    f"{message.author.mention}, posting invite links is not allowed."
                )
                await message.channel.send(embed=embed, delete_after=5)
                
                return True
            except:
                pass
        
        return False
    
    async def _check_mass_mentions(self, message: discord.Message) -> bool:
        """Check for mass mentions"""
        mention_count = len(message.mentions) + len(message.role_mentions)
        
        if mention_count > config.AutoMod.MAX_MENTIONS:
            try:
                await message.delete()
                
                embed = warning_embed(
                    "Mass Mentions",
                    f"{message.author.mention}, please don't mention too many users/roles at once."
                )
                await message.channel.send(embed=embed, delete_after=5)
                
                return True
            except:
                pass
        
        return False
    
    async def _check_everyone_pings(self, message: discord.Message) -> bool:
        """Check for @everyone/@here pings from non-authorized users"""
        # Get guild settings to check if everyone ping protection is enabled
        settings = await self.bot.db.get_guild_settings(message.guild.id)
        
        # Check if the feature is enabled
        if not getattr(settings, 'everyone_ping_protection', True):
            return False
        
        # Check if message contains @everyone or @here mentions
        if message.mention_everyone:
            # Check if user has manage messages permission (always allowed)
            if message.author.guild_permissions.manage_messages:
                return False
            
            # Check if user has any whitelisted roles
            whitelisted_roles = await self.bot.db.get_everyone_ping_whitelist(message.guild.id)
            user_role_ids = [role.id for role in message.author.roles]
            
            # If user has any whitelisted role, allow the ping
            if any(role_id in user_role_ids for role_id in whitelisted_roles):
                return False
            
            try:
                await message.delete()
                
                # Add a warning to the user
                await self.bot.db.add_warning(
                    message.author.id,
                    message.guild.id,
                    self.bot.user.id,
                    "Auto-mod: Attempted to ping @everyone/@here"
                )
                
                embed = warning_embed(
                    "Everyone Ping Blocked",
                    f"{message.author.mention}, you don't have permission to ping @everyone or @here."
                )
                await message.channel.send(embed=embed, delete_after=10)
                
                # Log the action to mod log if configured
                if settings.mod_log_channel:
                    log_channel = message.guild.get_channel(settings.mod_log_channel)
                    if log_channel:
                        log_embed = discord.Embed(
                            title="🚫 Everyone Ping Blocked",
                            color=config.Colors.WARNING,
                            timestamp=datetime.utcnow()
                        )
                        log_embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
                        log_embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                        log_embed.add_field(name="Action", value="Message deleted, warning added", inline=True)
                        log_embed.add_field(name="User Roles", value=", ".join([role.name for role in message.author.roles[1:]]) or "None", inline=True)
                        log_embed.add_field(name="Message Content", value=message.content[:1000] if message.content else "No content", inline=False)
                        
                        try:
                            await log_channel.send(embed=log_embed)
                        except:
                            pass
                
                return True
            except Exception as e:
                # If we can't delete the message, at least log it
                if settings.mod_log_channel:
                    log_channel = message.guild.get_channel(settings.mod_log_channel)
                    if log_channel:
                        log_embed = discord.Embed(
                            title="⚠️ Everyone Ping Detected (Could not delete)",
                            color=config.Colors.ERROR,
                            timestamp=datetime.utcnow()
                        )
                        log_embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=True)
                        log_embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                        log_embed.add_field(name="Error", value=str(e)[:500], inline=True)
                        
                        try:
                            await log_channel.send(embed=log_embed)
                        except:
                            pass
        
        return False
    
    @app_commands.command(name="automod", description="Configure auto-moderation settings")
    @app_commands.describe(
        feature="Feature to toggle",
        enabled="Enable or disable"
    )
    @app_commands.choices(feature=[
        app_commands.Choice(name="all", value="all"),
        app_commands.Choice(name="spam", value="spam"),
        app_commands.Choice(name="blacklist", value="blacklist"),
        app_commands.Choice(name="everyone-ping", value="everyone-ping")
    ])
    @is_moderator()
    async def automod(
        self,
        interaction: discord.Interaction,
        feature: str,
        enabled: bool
    ):
        """Configure auto-moderation settings"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        
        feature = feature.lower()
        
        if feature == "all":
            settings.automod_enabled = enabled
            feature_name = "Auto-moderation"
        elif feature == "spam":
            settings.spam_detection = enabled
            feature_name = "Spam detection"
        elif feature == "blacklist":
            settings.blacklist_enabled = enabled
            feature_name = "Blacklist filtering"
        elif feature == "everyone-ping":
            # We'll need to add this field to the database
            settings.everyone_ping_protection = enabled
            feature_name = "@everyone/@here ping protection"
        else:
            await interaction.response.send_message(
                "❌ Invalid feature. Choose from: all, spam, blacklist, everyone-ping",
                ephemeral=True
            )
            return
        
        await self.bot.db.update_guild_settings(settings)
        
        status = "enabled" if enabled else "disabled"
        embed = success_embed(
            "Auto-Mod Updated",
            f"{feature_name} has been {status}."
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="blacklist", description="Manage blacklisted words")
    @app_commands.describe(
        action="Add or remove word",
        word="Word to add/remove"
    )
    @is_moderator()
    async def blacklist(
        self,
        interaction: discord.Interaction,
        action: str,
        word: Optional[str] = None
    ):
        """Manage blacklisted words"""
        action = action.lower()
        
        if action == "list":
            blacklist = await self.bot.db.get_blacklist(interaction.guild.id)
            
            if not blacklist:
                await interaction.response.send_message(
                    "✅ No blacklisted words.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="Blacklisted Words",
                description="\n".join(f"• {word}" for word in blacklist),
                color=config.Colors.INFO
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif action == "add":
            if not word:
                await interaction.response.send_message(
                    "❌ Please provide a word to add.",
                    ephemeral=True
                )
                return
            
            await self.bot.db.add_blacklist_word(interaction.guild.id, word)
            
            embed = success_embed(
                "Word Blacklisted",
                f"Added '{word}' to the blacklist."
            )
            await interaction.response.send_message(embed=embed)
            
        elif action == "remove":
            if not word:
                await interaction.response.send_message(
                    "❌ Please provide a word to remove.",
                    ephemeral=True
                )
                return
            
            success = await self.bot.db.remove_blacklist_word(interaction.guild.id, word)
            
            if success:
                embed = success_embed(
                    "Word Removed",
                    f"Removed '{word}' from the blacklist."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"❌ '{word}' is not in the blacklist.",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Choose from: add, remove, list",
                ephemeral=True
            )
    
    @app_commands.command(name="automod-status", description="View current auto-moderation settings")
    @is_moderator()
    async def automod_status(self, interaction: discord.Interaction):
        """View current auto-moderation settings"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        
        embed = discord.Embed(
            title="🛡️ Auto-Moderation Status",
            color=config.Colors.INFO,
            timestamp=datetime.utcnow()
        )
        
        # Main toggle
        embed.add_field(
            name="Auto-Moderation",
            value="🟢 Enabled" if settings.automod_enabled else "🔴 Disabled",
            inline=True
        )
        
        # Individual features
        embed.add_field(
            name="Spam Detection",
            value="🟢 Enabled" if settings.spam_detection else "🔴 Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Blacklist Filtering",
            value="🟢 Enabled" if settings.blacklist_enabled else "🔴 Disabled",
            inline=True
        )
        
        embed.add_field(
            name="@everyone/@here Protection",
            value="🟢 Enabled" if getattr(settings, 'everyone_ping_protection', True) else "🔴 Disabled",
            inline=True
        )
        
        # Configuration info
        embed.add_field(
            name="Configuration",
            value=f"• Spam: {config.AutoMod.SPAM_MESSAGE_COUNT} messages in {config.AutoMod.SPAM_TIME_WINDOW}s\n"
                  f"• Caps threshold: {int(config.AutoMod.CAPS_THRESHOLD * 100)}%\n"
                  f"• Max mentions: {config.AutoMod.MAX_MENTIONS}",
            inline=False
        )
        
        # Get blacklist count
        blacklist = await self.bot.db.get_blacklist(interaction.guild.id)
        embed.add_field(
            name="Blacklisted Words",
            value=f"{len(blacklist)} words",
            inline=True
        )
        
        # Get whitelisted roles count
        whitelisted_roles = await self.bot.db.get_everyone_ping_whitelist(interaction.guild.id)
        embed.add_field(
            name="@everyone Whitelist",
            value=f"{len(whitelisted_roles)} roles",
            inline=True
        )
        
        embed.set_footer(text=f"Use /automod to configure settings")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="everyone-whitelist", description="Manage roles that can ping @everyone/@here")
    @app_commands.describe(
        action="Add, remove, or list whitelisted roles",
        role="Role to add/remove from whitelist"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="list", value="list"),
        app_commands.Choice(name="clear", value="clear")
    ])
    @is_moderator()
    async def everyone_whitelist(
        self,
        interaction: discord.Interaction,
        action: str,
        role: Optional[discord.Role] = None
    ):
        """Manage roles that can ping @everyone/@here"""
        action = action.lower()
        
        if action == "list":
            whitelisted_roles = await self.bot.db.get_everyone_ping_whitelist(interaction.guild.id)
            
            if not whitelisted_roles:
                embed = discord.Embed(
                    title="📋 Everyone Ping Whitelist",
                    description="No roles are whitelisted. Only users with 'Manage Messages' permission can ping @everyone/@here.",
                    color=config.Colors.INFO
                )
            else:
                role_mentions = []
                for role_id in whitelisted_roles:
                    role_obj = interaction.guild.get_role(role_id)
                    if role_obj:
                        role_mentions.append(role_obj.mention)
                    else:
                        role_mentions.append(f"<@&{role_id}> (deleted)")
                
                embed = discord.Embed(
                    title="📋 Everyone Ping Whitelist",
                    description="These roles can ping @everyone/@here:\n\n" + "\n".join(f"• {role}" for role in role_mentions),
                    color=config.Colors.INFO
                )
            
            embed.set_footer(text="Users with 'Manage Messages' permission are always allowed")
            await interaction.response.send_message(embed=embed)
            
        elif action == "add":
            if not role:
                await interaction.response.send_message(
                    "❌ Please specify a role to add to the whitelist.",
                    ephemeral=True
                )
                return
            
            success = await self.bot.db.add_everyone_ping_whitelist(interaction.guild.id, role.id)
            
            if success:
                embed = success_embed(
                    "Role Whitelisted",
                    f"Added {role.mention} to the @everyone ping whitelist.\n\nUsers with this role can now ping @everyone/@here."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"❌ {role.mention} is already in the whitelist.",
                    ephemeral=True
                )
                
        elif action == "remove":
            if not role:
                await interaction.response.send_message(
                    "❌ Please specify a role to remove from the whitelist.",
                    ephemeral=True
                )
                return
            
            success = await self.bot.db.remove_everyone_ping_whitelist(interaction.guild.id, role.id)
            
            if success:
                embed = success_embed(
                    "Role Removed",
                    f"Removed {role.mention} from the @everyone ping whitelist.\n\nUsers with this role can no longer ping @everyone/@here (unless they have other permissions)."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"❌ {role.mention} is not in the whitelist.",
                    ephemeral=True
                )
                
        elif action == "clear":
            count = await self.bot.db.clear_everyone_ping_whitelist(interaction.guild.id)
            
            if count > 0:
                embed = success_embed(
                    "Whitelist Cleared",
                    f"Removed {count} role(s) from the @everyone ping whitelist.\n\nOnly users with 'Manage Messages' permission can now ping @everyone/@here."
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "✅ The whitelist was already empty.",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "❌ Invalid action. Choose from: add, remove, list, clear",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
