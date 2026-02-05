"""
Moderation commands cog
Handles user moderation actions like ban, kick, mute, warn, etc.
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional

from utils.embeds import moderation_embed, success_embed, error_embed
from utils.checks import is_moderator, can_execute_action
from utils.helpers import parse_time, format_time
from utils.constants import ModAction
import config

class Moderation(commands.Cog):
    """Moderation commands for server management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        reason="Reason for the ban",
        delete_messages="Delete messages from the last N days (0-7)"
    )
    @is_moderator()
    async def ban(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = "No reason provided",
        delete_messages: Optional[int] = 0
    ):
        """Ban a user from the server"""
        # Check if action can be executed
        can_execute, error_msg = await can_execute_action(interaction, user, "ban")
        if not can_execute:
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Clamp delete_messages between 0 and 7
        delete_messages = max(0, min(7, delete_messages))
        
        try:
            # Send DM to user before banning
            try:
                dm_embed = error_embed(
                    "You have been banned",
                    f"**Server:** {interaction.guild.name}\n**Reason:** {reason}"
                )
                await user.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Ban the user
            await interaction.guild.ban(
                user,
                reason=f"{reason} | Banned by {interaction.user}",
                delete_message_days=delete_messages
            )
            
            # Log to database
            case_id = await self.bot.db.add_mod_log(
                interaction.guild.id,
                ModAction.BAN,
                user.id,
                interaction.user.id,
                reason
            )
            
            # Send confirmation
            embed = moderation_embed(
                ModAction.BAN,
                interaction.user,
                user,
                reason,
                case_id
            )
            await interaction.response.send_message(embed=embed)
            
            # Log to mod log channel
            await self._log_to_channel(interaction.guild, embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to ban this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for the unban"
    )
    @is_moderator()
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: Optional[str] = "No reason provided"
    ):
        """Unban a user from the server"""
        try:
            user_id = int(user_id)
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid user ID. Please provide a valid numeric ID.",
                ephemeral=True
            )
            return
        
        try:
            # Get user object
            user = await self.bot.fetch_user(user_id)
            
            # Unban the user
            await interaction.guild.unban(
                user,
                reason=f"{reason} | Unbanned by {interaction.user}"
            )
            
            # Log to database
            case_id = await self.bot.db.add_mod_log(
                interaction.guild.id,
                ModAction.UNBAN,
                user.id,
                interaction.user.id,
                reason
            )
            
            # Send confirmation
            embed = success_embed(
                "User Unbanned",
                f"**User:** {user.mention} ({user.id})\n**Reason:** {reason}\n**Case ID:** #{case_id}"
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.NotFound:
            await interaction.response.send_message(
                "❌ User not found or not banned.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to unban users.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="Reason for the kick"
    )
    @is_moderator()
    async def kick(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = "No reason provided"
    ):
        """Kick a user from the server"""
        # Check if action can be executed
        can_execute, error_msg = await can_execute_action(interaction, user, "kick")
        if not can_execute:
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        try:
            # Send DM to user before kicking
            try:
                dm_embed = error_embed(
                    "You have been kicked",
                    f"**Server:** {interaction.guild.name}\n**Reason:** {reason}"
                )
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Kick the user
            await interaction.guild.kick(
                user,
                reason=f"{reason} | Kicked by {interaction.user}"
            )
            
            # Log to database
            case_id = await self.bot.db.add_mod_log(
                interaction.guild.id,
                ModAction.KICK,
                user.id,
                interaction.user.id,
                reason
            )
            
            # Send confirmation
            embed = moderation_embed(
                ModAction.KICK,
                interaction.user,
                user,
                reason,
                case_id
            )
            await interaction.response.send_message(embed=embed)
            
            # Log to mod log channel
            await self._log_to_channel(interaction.guild, embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to kick this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="timeout", description="Timeout a user (Discord native)")
    @app_commands.describe(
        user="The user to timeout",
        duration="Duration (e.g., 1h, 30m, 1d)",
        reason="Reason for the timeout"
    )
    @is_moderator()
    async def timeout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: str,
        reason: Optional[str] = "No reason provided"
    ):
        """Timeout a user using Discord's native timeout feature"""
        # Check if action can be executed
        can_execute, error_msg = await can_execute_action(interaction, user, "timeout")
        if not can_execute:
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        # Parse duration
        time_delta = parse_time(duration)
        if not time_delta:
            await interaction.response.send_message(
                "❌ Invalid duration format. Use formats like: 1h, 30m, 1d",
                ephemeral=True
            )
            return
        
        # Discord timeout max is 28 days
        if time_delta.total_seconds() > 2419200:  # 28 days
            await interaction.response.send_message(
                "❌ Timeout duration cannot exceed 28 days.",
                ephemeral=True
            )
            return
        
        try:
            # Timeout the user
            until = datetime.utcnow() + time_delta
            await user.timeout(until, reason=f"{reason} | Timed out by {interaction.user}")
            
            # Log to database
            case_id = await self.bot.db.add_mod_log(
                interaction.guild.id,
                ModAction.TIMEOUT,
                user.id,
                interaction.user.id,
                f"{reason} | Duration: {format_time(int(time_delta.total_seconds()))}"
            )
            
            # Send confirmation
            embed = moderation_embed(
                ModAction.TIMEOUT,
                interaction.user,
                user,
                f"{reason}\n**Duration:** {format_time(int(time_delta.total_seconds()))}",
                case_id
            )
            await interaction.response.send_message(embed=embed)
            
            # Log to mod log channel
            await self._log_to_channel(interaction.guild, embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to timeout this user.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(
        user="The user to warn",
        reason="Reason for the warning"
    )
    @is_moderator()
    async def warn(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str
    ):
        """Warn a user"""
        # Check if action can be executed
        can_execute, error_msg = await can_execute_action(interaction, user, "warn")
        if not can_execute:
            await interaction.response.send_message(error_msg, ephemeral=True)
            return
        
        try:
            # Add warning to database
            warning_id = await self.bot.db.add_warning(
                user.id,
                interaction.guild.id,
                interaction.user.id,
                reason
            )
            
            # Log to mod logs
            case_id = await self.bot.db.add_mod_log(
                interaction.guild.id,
                ModAction.WARN,
                user.id,
                interaction.user.id,
                reason
            )
            
            # Get total warnings
            warnings = await self.bot.db.get_warnings(user.id, interaction.guild.id)
            
            # Send DM to user
            try:
                dm_embed = error_embed(
                    "You have been warned",
                    f"**Server:** {interaction.guild.name}\n**Reason:** {reason}\n**Total Warnings:** {len(warnings)}"
                )
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Send confirmation
            embed = moderation_embed(
                ModAction.WARN,
                interaction.user,
                user,
                reason,
                case_id
            )
            embed.add_field(name="Total Warnings", value=len(warnings), inline=False)
            await interaction.response.send_message(embed=embed)
            
            # Log to mod log channel
            await self._log_to_channel(interaction.guild, embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="warnings", description="View a user's warnings")
    @app_commands.describe(user="The user to check warnings for")
    @is_moderator()
    async def warnings(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """View warnings for a user"""
        warnings = await self.bot.db.get_warnings(user.id, interaction.guild.id)
        
        if not warnings:
            await interaction.response.send_message(
                f"✅ {user.mention} has no warnings.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"Warnings for {user.name}",
            description=f"Total warnings: {len(warnings)}",
            color=config.Colors.WARNING
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        for warning in warnings[:10]:  # Show last 10 warnings
            moderator = await self.bot.fetch_user(warning.moderator_id)
            embed.add_field(
                name=f"Warning #{warning.id}",
                value=f"**Reason:** {warning.reason}\n**Moderator:** {moderator.mention}\n**Date:** <t:{int(warning.timestamp.timestamp())}:R>",
                inline=False
            )
        
        if len(warnings) > 10:
            embed.set_footer(text=f"Showing 10 of {len(warnings)} warnings")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clearwarnings", description="Clear all warnings for a user")
    @app_commands.describe(user="The user to clear warnings for")
    @is_moderator()
    async def clearwarnings(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """Clear all warnings for a user"""
        warnings = await self.bot.db.get_warnings(user.id, interaction.guild.id)
        
        if not warnings:
            await interaction.response.send_message(
                f"✅ {user.mention} has no warnings to clear.",
                ephemeral=True
            )
            return
        
        await self.bot.db.clear_warnings(user.id, interaction.guild.id)
        
        # Log to mod logs
        case_id = await self.bot.db.add_mod_log(
            interaction.guild.id,
            ModAction.CLEAR_WARNINGS,
            user.id,
            interaction.user.id,
            f"Cleared {len(warnings)} warnings"
        )
        
        embed = success_embed(
            "Warnings Cleared",
            f"Cleared {len(warnings)} warnings for {user.mention}\n**Case ID:** #{case_id}"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="removewarn", description="Remove a specific warning")
    @app_commands.describe(warning_id="The ID of the warning to remove")
    @is_moderator()
    async def removewarn(
        self,
        interaction: discord.Interaction,
        warning_id: int
    ):
        """Remove a specific warning by ID"""
        success = await self.bot.db.remove_warning(warning_id)
        
        if success:
            embed = success_embed(
                "Warning Removed",
                f"Successfully removed warning #{warning_id}"
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ Warning #{warning_id} not found.",
                ephemeral=True
            )
    
    @app_commands.command(name="lock", description="Lock a channel")
    @app_commands.describe(channel="Channel to lock (defaults to current)")
    @is_moderator()
    async def lock(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ):
        """Lock a channel"""
        channel = channel or interaction.channel
        
        try:
            # Remove send message permission for @everyone
            await channel.set_permissions(
                interaction.guild.default_role,
                send_messages=False,
                reason=f"Channel locked by {interaction.user}"
            )
            
            embed = success_embed(
                "Channel Locked",
                f"{channel.mention} has been locked. Only moderators can send messages."
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage this channel.",
                ephemeral=True
            )
    
    @app_commands.command(name="unlock", description="Unlock a channel")
    @app_commands.describe(channel="Channel to unlock (defaults to current)")
    @is_moderator()
    async def unlock(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ):
        """Unlock a channel"""
        channel = channel or interaction.channel
        
        try:
            # Restore send message permission for @everyone
            await channel.set_permissions(
                interaction.guild.default_role,
                send_messages=None,
                reason=f"Channel unlocked by {interaction.user}"
            )
            
            embed = success_embed(
                "Channel Unlocked",
                f"{channel.mention} has been unlocked."
            )
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage this channel.",
                ephemeral=True
            )
    
    @app_commands.command(name="slowmode", description="Set channel slowmode")
    @app_commands.describe(
        seconds="Slowmode delay in seconds (0 to disable)",
        channel="Channel to set slowmode (defaults to current)"
    )
    @is_moderator()
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: int,
        channel: Optional[discord.TextChannel] = None
    ):
        """Set slowmode for a channel"""
        channel = channel or interaction.channel
        
        if seconds < 0 or seconds > 21600:
            await interaction.response.send_message(
                "❌ Slowmode must be between 0 and 21600 seconds (6 hours).",
                ephemeral=True
            )
            return
        
        try:
            await channel.edit(
                slowmode_delay=seconds,
                reason=f"Slowmode set by {interaction.user}"
            )
            
            if seconds == 0:
                embed = success_embed(
                    "Slowmode Disabled",
                    f"Slowmode has been disabled in {channel.mention}"
                )
            else:
                from utils.helpers import format_time
                embed = success_embed(
                    "Slowmode Enabled",
                    f"Slowmode set to {format_time(seconds)} in {channel.mention}"
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage this channel.",
                ephemeral=True
            )
    
    @app_commands.command(name="nuke", description="Clone and delete a channel (clears all messages)")
    @app_commands.describe(channel="Channel to nuke (defaults to current)")
    @is_moderator()
    async def nuke(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ):
        """Nuke a channel by cloning and deleting it"""
        channel = channel or interaction.channel
        
        try:
            # Clone the channel
            new_channel = await channel.clone(reason=f"Channel nuked by {interaction.user}")
            
            # Delete the old channel
            await channel.delete(reason=f"Channel nuked by {interaction.user}")
            
            # Send confirmation in new channel
            embed = success_embed(
                "Channel Nuked",
                f"Channel has been nuked by {interaction.user.mention}"
            )
            await new_channel.send(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage channels.",
                ephemeral=True
            )
    
    @app_commands.command(name="role", description="Manage user roles")
    @app_commands.describe(
        action="Add or remove role",
        user="User to modify",
        role="Role to add/remove"
    )
    @is_moderator()
    async def role(
        self,
        interaction: discord.Interaction,
        action: str,
        user: discord.Member,
        role: discord.Role
    ):
        """Add or remove a role from a user"""
        if action.lower() not in ['add', 'remove']:
            await interaction.response.send_message(
                "❌ Action must be 'add' or 'remove'.",
                ephemeral=True
            )
            return
        
        # Check role hierarchy
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ I cannot manage this role as it's higher than or equal to my highest role.",
                ephemeral=True
            )
            return
        
        if role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ You cannot manage this role as it's higher than or equal to your highest role.",
                ephemeral=True
            )
            return
        
        try:
            if action.lower() == 'add':
                if role in user.roles:
                    await interaction.response.send_message(
                        f"❌ {user.mention} already has the {role.mention} role.",
                        ephemeral=True
                    )
                    return
                
                await user.add_roles(role, reason=f"Role added by {interaction.user}")
                embed = success_embed(
                    "Role Added",
                    f"Added {role.mention} to {user.mention}"
                )
            else:  # remove
                if role not in user.roles:
                    await interaction.response.send_message(
                        f"❌ {user.mention} doesn't have the {role.mention} role.",
                        ephemeral=True
                    )
                    return
                
                await user.remove_roles(role, reason=f"Role removed by {interaction.user}")
                embed = success_embed(
                    "Role Removed",
                    f"Removed {role.mention} from {user.mention}"
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles.",
                ephemeral=True
            )
    
    @app_commands.command(name="nickname", description="Change a user's nickname")
    @app_commands.describe(
        user="User to change nickname",
        nickname="New nickname (leave empty to reset)"
    )
    @is_moderator()
    async def nickname(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        nickname: Optional[str] = None
    ):
        """Change a user's nickname"""
        # Check hierarchy
        if user.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(
                "❌ I cannot change the nickname of someone with a higher or equal role.",
                ephemeral=True
            )
            return
        
        try:
            old_nick = user.nick or user.name
            await user.edit(nick=nickname, reason=f"Nickname changed by {interaction.user}")
            
            if nickname:
                embed = success_embed(
                    "Nickname Changed",
                    f"Changed {user.mention}'s nickname from **{old_nick}** to **{nickname}**"
                )
            else:
                embed = success_embed(
                    "Nickname Reset",
                    f"Reset {user.mention}'s nickname"
                )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to change nicknames.",
                ephemeral=True
            )
    
    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user",
        contains="Only delete messages containing this text",
        bots="Only delete bot messages",
        embeds="Only delete messages with embeds",
        files="Only delete messages with attachments"
    )
    @is_moderator()
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: int,
        user: Optional[discord.Member] = None,
        contains: Optional[str] = None,
        bots: Optional[bool] = False,
        embeds: Optional[bool] = False,
        files: Optional[bool] = False
    ):
        """Delete multiple messages with optional filters"""
        if amount < 1 or amount > 100:
            await interaction.response.send_message(
                "❌ Amount must be between 1 and 100.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        def check_message(msg):
            """Check if message matches filters"""
            if user and msg.author != user:
                return False
            if contains and contains.lower() not in msg.content.lower():
                return False
            if bots and not msg.author.bot:
                return False
            if embeds and not msg.embeds:
                return False
            if files and not msg.attachments:
                return False
            return True
        
        try:
            deleted = await interaction.channel.purge(limit=amount, check=check_message)
            
            # Create filter description
            filters = []
            if user:
                filters.append(f"from {user.mention}")
            if contains:
                filters.append(f"containing '{contains}'")
            if bots:
                filters.append("from bots")
            if embeds:
                filters.append("with embeds")
            if files:
                filters.append("with files")
            
            filter_text = " ".join(filters) if filters else ""
            
            embed = success_embed(
                "Messages Purged",
                f"Deleted {len(deleted)} messages {filter_text}"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to delete messages.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    async def _log_to_channel(self, guild: discord.Guild, embed: discord.Embed):
        """Log moderation action to the configured log channel"""
        try:
            settings = await self.bot.db.get_guild_settings(guild.id)
            if settings.mod_log_channel:
                channel = guild.get_channel(settings.mod_log_channel)
                if channel:
                    await channel.send(embed=embed)
        except:
            pass  # Silently fail if logging fails

async def setup(bot):
    await bot.add_cog(Moderation(bot))
