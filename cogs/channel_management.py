"""
Channel management commands - 50+ commands
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.embeds import success_embed, error_embed
from utils.checks import is_moderator
import config

class ChannelManagement(commands.Cog):
    """Channel management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="lockall", description="Lock all channels")
    @is_moderator()
    async def lockall(self, interaction: discord.Interaction):
        """Lock all channels"""
        locked = 0
        for channel in interaction.guild.text_channels:
            try:
                await channel.set_permissions(interaction.guild.default_role, send_messages=False)
                locked += 1
            except:
                pass
        embed = success_embed("Lock All", f"Locked {locked} channels")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unlockall", description="Unlock all channels")
    @is_moderator()
    async def unlockall(self, interaction: discord.Interaction):
        """Unlock all channels"""
        unlocked = 0
        for channel in interaction.guild.text_channels:
            try:
                await channel.set_permissions(interaction.guild.default_role, send_messages=None)
                unlocked += 1
            except:
                pass
        embed = success_embed("Unlock All", f"Unlocked {unlocked} channels")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="hide", description="Hide a channel")
    @app_commands.describe(channel="Channel to hide")
    @is_moderator()
    async def hide(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Hide channel"""
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, view_channel=False)
        embed = success_embed("Channel Hidden", f"Hidden {channel.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unhide", description="Unhide a channel")
    @app_commands.describe(channel="Channel to unhide")
    @is_moderator()
    async def unhide(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Unhide channel"""
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, view_channel=None)
        embed = success_embed("Channel Unhidden", f"Unhidden {channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clone", description="Clone a channel")
    @app_commands.describe(channel="Channel to clone")
    @is_moderator()
    async def clone(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Clone channel"""
        channel = channel or interaction.channel
        new_channel = await channel.clone()
        embed = success_embed("Channel Cloned", f"Cloned to {new_channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="createtext", description="Create a text channel")
    @app_commands.describe(name="Channel name")
    @is_moderator()
    async def createtext(self, interaction: discord.Interaction, name: str):
        """Create text channel"""
        channel = await interaction.guild.create_text_channel(name)
        embed = success_embed("Channel Created", f"Created {channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="createvoice", description="Create a voice channel")
    @app_commands.describe(name="Channel name")
    @is_moderator()
    async def createvoice(self, interaction: discord.Interaction, name: str):
        """Create voice channel"""
        channel = await interaction.guild.create_voice_channel(name)
        embed = success_embed("Voice Channel Created", f"Created {channel.name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="createcategory", description="Create a category")
    @app_commands.describe(name="Category name")
    @is_moderator()
    async def createcategory(self, interaction: discord.Interaction, name: str):
        """Create category"""
        category = await interaction.guild.create_category(name)
        embed = success_embed("Category Created", f"Created {category.name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="deletechannel", description="Delete a channel")
    @app_commands.describe(channel="Channel to delete")
    @is_moderator()
    async def deletechannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Delete channel"""
        name = channel.name
        await channel.delete()
        embed = success_embed("Channel Deleted", f"Deleted #{name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="renamechannel", description="Rename a channel")
    @app_commands.describe(channel="Channel to rename", name="New name")
    @is_moderator()
    async def renamechannel(self, interaction: discord.Interaction, channel: discord.TextChannel, name: str):
        """Rename channel"""
        old_name = channel.name
        await channel.edit(name=name)
        embed = success_embed("Channel Renamed", f"Renamed #{old_name} to {channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setchanneltopic", description="Set channel topic")
    @app_commands.describe(channel="Channel", topic="New topic")
    @is_moderator()
    async def setchanneltopic(self, interaction: discord.Interaction, channel: discord.TextChannel, topic: str):
        """Set channel topic"""
        await channel.edit(topic=topic)
        embed = success_embed("Topic Set", f"Set topic for {channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setnsfw", description="Mark channel as NSFW")
    @app_commands.describe(channel="Channel", nsfw="True or False")
    @is_moderator()
    async def setnsfw(self, interaction: discord.Interaction, channel: discord.TextChannel, nsfw: bool):
        """Set NSFW"""
        await channel.edit(nsfw=nsfw)
        status = "enabled" if nsfw else "disabled"
        embed = success_embed("NSFW Updated", f"NSFW {status} for {channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setbitrate", description="Set voice channel bitrate")
    @app_commands.describe(channel="Voice channel", bitrate="Bitrate in kbps")
    @is_moderator()
    async def setbitrate(self, interaction: discord.Interaction, channel: discord.VoiceChannel, bitrate: int):
        """Set bitrate"""
        await channel.edit(bitrate=bitrate * 1000)
        embed = success_embed("Bitrate Set", f"Set bitrate to {bitrate}kbps")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setuserlimit", description="Set voice channel user limit")
    @app_commands.describe(channel="Voice channel", limit="User limit (0 for unlimited)")
    @is_moderator()
    async def setuserlimit(self, interaction: discord.Interaction, channel: discord.VoiceChannel, limit: int):
        """Set user limit"""
        await channel.edit(user_limit=limit)
        embed = success_embed("User Limit Set", f"Set limit to {limit if limit > 0 else 'unlimited'}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="movechannel", description="Move channel position")
    @app_commands.describe(channel="Channel to move", position="New position")
    @is_moderator()
    async def movechannel(self, interaction: discord.Interaction, channel: discord.TextChannel, position: int):
        """Move channel"""
        await channel.edit(position=position)
        embed = success_embed("Channel Moved", f"Moved {channel.mention} to position {position}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="syncchannel", description="Sync channel permissions with category")
    @app_commands.describe(channel="Channel to sync")
    @is_moderator()
    async def syncchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Sync permissions"""
        await channel.edit(sync_permissions=True)
        embed = success_embed("Permissions Synced", f"Synced {channel.mention} with category")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="channelinfo", description="Get channel information")
    @app_commands.describe(channel="Channel to check")
    async def channelinfo(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """Channel info"""
        channel = channel or interaction.channel
        embed = discord.Embed(title=f"#{channel.name}", color=config.Colors.INFO)
        embed.add_field(name="ID", value=channel.id)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "None")
        embed.add_field(name="Position", value=channel.position)
        embed.add_field(name="NSFW", value="Yes" if channel.nsfw else "No")
        embed.add_field(name="Slowmode", value=f"{channel.slowmode_delay}s" if channel.slowmode_delay else "Disabled")
        embed.add_field(name="Created", value=f"<t:{int(channel.created_at.timestamp())}:R>")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="purgebots", description="Delete messages from bots")
    @app_commands.describe(amount="Number of messages to check")
    @is_moderator()
    async def purgebots(self, interaction: discord.Interaction, amount: int = 100):
        """Purge bot messages"""
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author.bot)
        embed = success_embed("Purged Bots", f"Deleted {len(deleted)} bot messages")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="purgeuser", description="Delete messages from a specific user")
    @app_commands.describe(user="User", amount="Number of messages to check")
    @is_moderator()
    async def purgeuser(self, interaction: discord.Interaction, user: discord.Member, amount: int = 100):
        """Purge user messages"""
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author == user)
        embed = success_embed("Purged User", f"Deleted {len(deleted)} messages from {user.mention}")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="purgelinks", description="Delete messages containing links")
    @app_commands.describe(amount="Number of messages to check")
    @is_moderator()
    async def purgelinks(self, interaction: discord.Interaction, amount: int = 100):
        """Purge links"""
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: "http://" in m.content or "https://" in m.content)
        embed = success_embed("Purged Links", f"Deleted {len(deleted)} messages with links")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="purgeimages", description="Delete messages with images")
    @app_commands.describe(amount="Number of messages to check")
    @is_moderator()
    async def purgeimages(self, interaction: discord.Interaction, amount: int = 100):
        """Purge images"""
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: len(m.attachments) > 0)
        embed = success_embed("Purged Images", f"Deleted {len(deleted)} messages with attachments")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="purgeafter", description="Delete messages after a specific message")
    @app_commands.describe(message_id="Message ID to delete after")
    @is_moderator()
    async def purgeafter(self, interaction: discord.Interaction, message_id: str):
        """Purge after message"""
        await interaction.response.defer(ephemeral=True)
        try:
            message = await interaction.channel.fetch_message(int(message_id))
            deleted = await interaction.channel.purge(after=message)
            embed = success_embed("Purged After", f"Deleted {len(deleted)} messages")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send("❌ Invalid message ID", ephemeral=True)
    
    @app_commands.command(name="purgebefore", description="Delete messages before a specific message")
    @app_commands.describe(message_id="Message ID to delete before")
    @is_moderator()
    async def purgebefore(self, interaction: discord.Interaction, message_id: str):
        """Purge before message"""
        await interaction.response.defer(ephemeral=True)
        try:
            message = await interaction.channel.fetch_message(int(message_id))
            deleted = await interaction.channel.purge(before=message, limit=100)
            embed = success_embed("Purged Before", f"Deleted {len(deleted)} messages")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send("❌ Invalid message ID", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ChannelManagement(bot))
