"""
Advanced moderation commands - Part 1
Adds 50+ additional moderation commands
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Optional
import asyncio

from utils.embeds import success_embed, error_embed, info_embed
from utils.checks import is_moderator
from utils.helpers import parse_time, format_time
import config

class AdvancedModeration(commands.Cog):
    """Advanced moderation commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="massban", description="Ban multiple users at once")
    @app_commands.describe(user_ids="User IDs separated by spaces", reason="Reason for bans")
    @is_moderator()
    async def massban(self, interaction: discord.Interaction, user_ids: str, reason: str = "Mass ban"):
        """Mass ban users"""
        await interaction.response.defer()
        ids = user_ids.split()
        banned = []
        failed = []
        
        for user_id in ids:
            try:
                user = await self.bot.fetch_user(int(user_id))
                await interaction.guild.ban(user, reason=reason)
                banned.append(user_id)
            except:
                failed.append(user_id)
        
        embed = success_embed("Mass Ban Complete", f"Banned: {len(banned)}\nFailed: {len(failed)}")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="masskick", description="Kick multiple users at once")
    @app_commands.describe(users="Mention users to kick", reason="Reason")
    @is_moderator()
    async def masskick(self, interaction: discord.Interaction, users: str, reason: str = "Mass kick"):
        """Mass kick users"""
        await interaction.response.defer()
        kicked = 0
        for member in interaction.message.mentions if hasattr(interaction, 'message') else []:
            try:
                await member.kick(reason=reason)
                kicked += 1
            except:
                pass
        embed = success_embed("Mass Kick", f"Kicked {kicked} users")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="softban", description="Ban and immediately unban to delete messages")
    @app_commands.describe(user="User to softban", reason="Reason")
    @is_moderator()
    async def softban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Softban"):
        """Softban a user"""
        try:
            await interaction.guild.ban(user, reason=reason, delete_message_days=7)
            await interaction.guild.unban(user, reason="Softban unban")
            embed = success_embed("Softban Complete", f"Softbanned {user.mention}")
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)
    
    @app_commands.command(name="tempban", description="Temporarily ban a user")
    @app_commands.describe(user="User to ban", duration="Duration (e.g., 1d, 12h)", reason="Reason")
    @is_moderator()
    async def tempban(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "Temp ban"):
        """Temporarily ban a user"""
        time_delta = parse_time(duration)
        if not time_delta:
            await interaction.response.send_message("❌ Invalid duration", ephemeral=True)
            return
        
        await interaction.guild.ban(user, reason=reason)
        embed = success_embed("Temp Ban", f"Banned {user.mention} for {format_time(int(time_delta.total_seconds()))}")
        await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(time_delta.total_seconds())
        try:
            await interaction.guild.unban(user, reason="Temp ban expired")
        except:
            pass
    
    @app_commands.command(name="tempmute", description="Temporarily mute a user")
    @app_commands.describe(user="User to mute", duration="Duration", reason="Reason")
    @is_moderator()
    async def tempmute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "Temp mute"):
        """Temporarily mute a user"""
        time_delta = parse_time(duration)
        if not time_delta:
            await interaction.response.send_message("❌ Invalid duration", ephemeral=True)
            return
        
        until = datetime.utcnow() + time_delta
        await user.timeout(until, reason=reason)
        embed = success_embed("Temp Mute", f"Muted {user.mention} for {format_time(int(time_delta.total_seconds()))}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(user="User to unmute")
    @is_moderator()
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        """Unmute a user"""
        await user.timeout(None)
        embed = success_embed("Unmuted", f"Unmuted {user.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="voiceban", description="Ban user from voice channels")
    @app_commands.describe(user="User to voice ban")
    @is_moderator()
    async def voiceban(self, interaction: discord.Interaction, user: discord.Member):
        """Ban from voice"""
        await user.edit(mute=True, deafen=True)
        embed = success_embed("Voice Ban", f"Banned {user.mention} from voice")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="voiceunban", description="Unban user from voice channels")
    @app_commands.describe(user="User to voice unban")
    @is_moderator()
    async def voiceunban(self, interaction: discord.Interaction, user: discord.Member):
        """Unban from voice"""
        await user.edit(mute=False, deafen=False)
        embed = success_embed("Voice Unban", f"Unbanned {user.mention} from voice")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="voicekick", description="Kick user from voice channel")
    @app_commands.describe(user="User to kick from voice")
    @is_moderator()
    async def voicekick(self, interaction: discord.Interaction, user: discord.Member):
        """Kick from voice"""
        if user.voice:
            await user.move_to(None)
            embed = success_embed("Voice Kick", f"Kicked {user.mention} from voice")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ User not in voice", ephemeral=True)
    
    @app_commands.command(name="voicemute", description="Mute user in voice")
    @app_commands.describe(user="User to mute")
    @is_moderator()
    async def voicemute(self, interaction: discord.Interaction, user: discord.Member):
        """Voice mute"""
        await user.edit(mute=True)
        embed = success_embed("Voice Mute", f"Muted {user.mention} in voice")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="voiceunmute", description="Unmute user in voice")
    @app_commands.describe(user="User to unmute")
    @is_moderator()
    async def voiceunmute(self, interaction: discord.Interaction, user: discord.Member):
        """Voice unmute"""
        await user.edit(mute=False)
        embed = success_embed("Voice Unmute", f"Unmuted {user.mention} in voice")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="deafen", description="Deafen user in voice")
    @app_commands.describe(user="User to deafen")
    @is_moderator()
    async def deafen(self, interaction: discord.Interaction, user: discord.Member):
        """Deafen user"""
        await user.edit(deafen=True)
        embed = success_embed("Deafened", f"Deafened {user.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="undeafen", description="Undeafen user in voice")
    @app_commands.describe(user="User to undeafen")
    @is_moderator()
    async def undeafen(self, interaction: discord.Interaction, user: discord.Member):
        """Undeafen user"""
        await user.edit(deafen=False)
        embed = success_embed("Undeafened", f"Undeafened {user.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="moveall", description="Move all users from one voice channel to another")
    @app_commands.describe(from_channel="Source voice channel", to_channel="Destination voice channel")
    @is_moderator()
    async def moveall(self, interaction: discord.Interaction, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
        """Move all users"""
        moved = 0
        for member in from_channel.members:
            try:
                await member.move_to(to_channel)
                moved += 1
            except:
                pass
        embed = success_embed("Move All", f"Moved {moved} users")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="disconnectall", description="Disconnect all users from a voice channel")
    @app_commands.describe(channel="Voice channel to clear")
    @is_moderator()
    async def disconnectall(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Disconnect all from voice"""
        disconnected = 0
        for member in channel.members:
            try:
                await member.move_to(None)
                disconnected += 1
            except:
                pass
        embed = success_embed("Disconnect All", f"Disconnected {disconnected} users")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="muteall", description="Mute all users in a voice channel")
    @app_commands.describe(channel="Voice channel")
    @is_moderator()
    async def muteall(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Mute all in voice"""
        muted = 0
        for member in channel.members:
            try:
                await member.edit(mute=True)
                muted += 1
            except:
                pass
        embed = success_embed("Mute All", f"Muted {muted} users")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unmuteall", description="Unmute all users in a voice channel")
    @app_commands.describe(channel="Voice channel")
    @is_moderator()
    async def unmuteall(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Unmute all in voice"""
        unmuted = 0
        for member in channel.members:
            try:
                await member.edit(mute=False)
                unmuted += 1
            except:
                pass
        embed = success_embed("Unmute All", f"Unmuted {unmuted} users")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedModeration(bot))
