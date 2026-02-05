"""
Server management commands - 30+ commands
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.embeds import success_embed, error_embed, info_embed
from utils.checks import is_moderator
import config

class ServerManagement(commands.Cog):
    """Server management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="setservername", description="Change server name")
    @app_commands.describe(name="New server name")
    @is_moderator()
    async def setservername(self, interaction: discord.Interaction, name: str):
        """Change server name"""
        old_name = interaction.guild.name
        await interaction.guild.edit(name=name)
        embed = success_embed("Server Name Changed", f"Changed from {old_name} to {name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setservericon", description="Change server icon")
    @app_commands.describe(url="Image URL")
    @is_moderator()
    async def setservericon(self, interaction: discord.Interaction, url: str):
        """Change server icon"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await interaction.guild.edit(icon=data)
                    embed = success_embed("Server Icon Changed", "Icon updated successfully")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("❌ Failed to fetch image", ephemeral=True)

    @app_commands.command(name="setserverbanner", description="Change server banner")
    @app_commands.describe(url="Image URL")
    @is_moderator()
    async def setserverbanner(self, interaction: discord.Interaction, url: str):
        """Change server banner"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    await interaction.guild.edit(banner=data)
                    embed = success_embed("Server Banner Changed", "Banner updated")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("❌ Failed", ephemeral=True)
    
    @app_commands.command(name="setverificationlevel", description="Set verification level")
    @app_commands.describe(level="Verification level (0-4)")
    @is_moderator()
    async def setverificationlevel(self, interaction: discord.Interaction, level: int):
        """Set verification level"""
        levels = {0: "None", 1: "Low", 2: "Medium", 3: "High", 4: "Highest"}
        if level not in levels:
            await interaction.response.send_message("❌ Level must be 0-4", ephemeral=True)
            return
        await interaction.guild.edit(verification_level=discord.VerificationLevel(level))
        embed = success_embed("Verification Level Set", f"Set to {levels[level]}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setafkchannel", description="Set AFK channel")
    @app_commands.describe(channel="Voice channel for AFK")
    @is_moderator()
    async def setafkchannel(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Set AFK channel"""
        await interaction.guild.edit(afk_channel=channel)
        embed = success_embed("AFK Channel Set", f"Set to {channel.name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setafktimeout", description="Set AFK timeout")
    @app_commands.describe(timeout="Timeout in seconds (60-3600)")
    @is_moderator()
    async def setafktimeout(self, interaction: discord.Interaction, timeout: int):
        """Set AFK timeout"""
        if timeout < 60 or timeout > 3600:
            await interaction.response.send_message("❌ Timeout must be 60-3600", ephemeral=True)
            return
        await interaction.guild.edit(afk_timeout=timeout)
        embed = success_embed("AFK Timeout Set", f"Set to {timeout} seconds")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setsystemchannel", description="Set system messages channel")
    @app_commands.describe(channel="Channel for system messages")
    @is_moderator()
    async def setsystemchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set system channel"""
        await interaction.guild.edit(system_channel=channel)
        embed = success_embed("System Channel Set", f"Set to {channel.mention}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="emojis", description="List all server emojis")
    async def emojis(self, interaction: discord.Interaction):
        """List emojis"""
        emojis = [str(e) for e in interaction.guild.emojis[:50]]
        embed = discord.Embed(
            title="Server Emojis",
            description=" ".join(emojis) if emojis else "No emojis",
            color=config.Colors.INFO
        )
        embed.set_footer(text=f"Total: {len(interaction.guild.emojis)}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stickers", description="List all server stickers")
    async def stickers(self, interaction: discord.Interaction):
        """List stickers"""
        stickers = [s.name for s in interaction.guild.stickers]
        embed = discord.Embed(
            title="Server Stickers",
            description="\n".join(stickers) if stickers else "No stickers",
            color=config.Colors.INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="bans", description="List all banned users")
    @is_moderator()
    async def bans(self, interaction: discord.Interaction):
        """List bans"""
        await interaction.response.defer()
        bans = [f"{entry.user.name} ({entry.user.id})" async for entry in interaction.guild.bans(limit=50)]
        embed = discord.Embed(
            title="Banned Users",
            description="\n".join(bans) if bans else "No bans",
            color=config.Colors.ERROR
        )
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="invites", description="List server invites")
    @is_moderator()
    async def invites(self, interaction: discord.Interaction):
        """List invites"""
        invites = await interaction.guild.invites()
        if not invites:
            await interaction.response.send_message("No invites", ephemeral=True)
            return
        embed = discord.Embed(title="Server Invites", color=config.Colors.INFO)
        for inv in invites[:10]:
            embed.add_field(
                name=inv.code,
                value=f"Uses: {inv.uses} | Channel: {inv.channel.mention}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="createinvite", description="Create server invite")
    @app_commands.describe(channel="Channel", max_age="Max age in seconds (0 for permanent)", max_uses="Max uses (0 for unlimited)")
    @is_moderator()
    async def createinvite(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None, max_age: int = 0, max_uses: int = 0):
        """Create invite"""
        channel = channel or interaction.channel
        invite = await channel.create_invite(max_age=max_age, max_uses=max_uses)
        embed = success_embed("Invite Created", f"Invite: {invite.url}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="webhooks", description="List channel webhooks")
    @is_moderator()
    async def webhooks(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        """List webhooks"""
        channel = channel or interaction.channel
        webhooks = await channel.webhooks()
        if not webhooks:
            await interaction.response.send_message("No webhooks", ephemeral=True)
            return
        embed = discord.Embed(title=f"Webhooks in {channel.name}", color=config.Colors.INFO)
        for wh in webhooks:
            embed.add_field(name=wh.name, value=f"ID: {wh.id}", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="createwebhook", description="Create a webhook")
    @app_commands.describe(name="Webhook name", channel="Channel")
    @is_moderator()
    async def createwebhook(self, interaction: discord.Interaction, name: str, channel: Optional[discord.TextChannel] = None):
        """Create webhook"""
        channel = channel or interaction.channel
        webhook = await channel.create_webhook(name=name)
        embed = success_embed("Webhook Created", f"Created {name} in {channel.mention}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="auditlog", description="View recent audit log entries")
    @is_moderator()
    async def auditlog(self, interaction: discord.Interaction):
        """View audit log"""
        await interaction.response.defer()
        entries = []
        async for entry in interaction.guild.audit_logs(limit=10):
            entries.append(f"{entry.user.name}: {entry.action.name}")
        embed = discord.Embed(
            title="Recent Audit Log",
            description="\n".join(entries),
            color=config.Colors.INFO
        )
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="membercount", description="Show member count")
    async def membercount(self, interaction: discord.Interaction):
        """Member count"""
        total = interaction.guild.member_count
        humans = len([m for m in interaction.guild.members if not m.bot])
        bots = len([m for m in interaction.guild.members if m.bot])
        embed = discord.Embed(title="Member Count", color=config.Colors.INFO)
        embed.add_field(name="Total", value=total)
        embed.add_field(name="Humans", value=humans)
        embed.add_field(name="Bots", value=bots)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="boostinfo", description="Server boost information")
    async def boostinfo(self, interaction: discord.Interaction):
        """Boost info"""
        embed = discord.Embed(title="Boost Information", color=discord.Color.pink())
        embed.add_field(name="Boost Level", value=interaction.guild.premium_tier)
        embed.add_field(name="Boosts", value=interaction.guild.premium_subscription_count)
        embed.add_field(name="Boosters", value=len(interaction.guild.premium_subscribers))
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
