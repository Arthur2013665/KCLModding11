"""
Member management commands - 30+ commands
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime

from utils.embeds import success_embed, error_embed, info_embed
from utils.checks import is_moderator
import config

class MemberManagement(commands.Cog):
    """Member management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="whois", description="Get detailed user information")
    @app_commands.describe(user="User to check")
    async def whois(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Detailed user info"""
        user = user or interaction.user
        embed = discord.Embed(title=f"{user.name}#{user.discriminator}", color=user.color)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=user.id, inline=False)
        embed.add_field(name="Nickname", value=user.nick or "None")
        embed.add_field(name="Status", value=str(user.status).title())
        embed.add_field(name="Joined Server", value=f"<t:{int(user.joined_at.timestamp())}:R>")
        embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:R>")
        embed.add_field(name="Roles", value=f"{len(user.roles)-1}")
        embed.add_field(name="Top Role", value=user.top_role.mention)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="members", description="List all server members")
    async def members(self, interaction: discord.Interaction):
        """List members"""
        members = [m.mention for m in interaction.guild.members[:50]]
        embed = discord.Embed(title="Server Members", description="\n".join(members), color=config.Colors.INFO)
        embed.set_footer(text=f"Total: {interaction.guild.member_count}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="bots", description="List all bots")
    async def bots(self, interaction: discord.Interaction):
        """List bots"""
        bots = [m.mention for m in interaction.guild.members if m.bot]
        embed = discord.Embed(title="Server Bots", description="\n".join(bots) if bots else "No bots", color=config.Colors.INFO)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="humans", description="List all human members")
    async def humans(self, interaction: discord.Interaction):
        """List humans"""
        humans = [m.mention for m in interaction.guild.members if not m.bot][:50]
        embed = discord.Embed(title="Human Members", description="\n".join(humans), color=config.Colors.INFO)
        embed.set_footer(text=f"Total: {len([m for m in interaction.guild.members if not m.bot])}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mods", description="List all moderators")
    async def mods(self, interaction: discord.Interaction):
        """List moderators"""
        mods = [m.mention for m in interaction.guild.members if m.guild_permissions.manage_messages]
        embed = discord.Embed(title="Moderators", description="\n".join(mods) if mods else "No mods", color=config.Colors.INFO)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="admins", description="List all administrators")
    async def admins(self, interaction: discord.Interaction):
        """List admins"""
        admins = [m.mention for m in interaction.guild.members if m.guild_permissions.administrator]
        embed = discord.Embed(title="Administrators", description="\n".join(admins) if admins else "No admins", color=config.Colors.INFO)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="boosters", description="List all server boosters")
    async def boosters(self, interaction: discord.Interaction):
        """List boosters"""
        boosters = [m.mention for m in interaction.guild.premium_subscribers]
        embed = discord.Embed(title="Server Boosters", description="\n".join(boosters) if boosters else "No boosters", color=discord.Color.pink())
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="oldest", description="Show oldest members")
    async def oldest(self, interaction: discord.Interaction):
        """Oldest members"""
        members = sorted(interaction.guild.members, key=lambda m: m.joined_at)[:10]
        embed = discord.Embed(title="Oldest Members", color=config.Colors.INFO)
        for i, m in enumerate(members, 1):
            embed.add_field(name=f"{i}. {m.name}", value=f"Joined <t:{int(m.joined_at.timestamp())}:R>", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="newest", description="Show newest members")
    async def newest(self, interaction: discord.Interaction):
        """Newest members"""
        members = sorted(interaction.guild.members, key=lambda m: m.joined_at, reverse=True)[:10]
        embed = discord.Embed(title="Newest Members", color=config.Colors.INFO)
        for i, m in enumerate(members, 1):
            embed.add_field(name=f"{i}. {m.name}", value=f"Joined <t:{int(m.joined_at.timestamp())}:R>", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="joinposition", description="Check join position")
    @app_commands.describe(user="User to check")
    async def joinposition(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Join position"""
        user = user or interaction.user
        members = sorted(interaction.guild.members, key=lambda m: m.joined_at)
        position = members.index(user) + 1
        embed = discord.Embed(
            title="Join Position",
            description=f"{user.mention} was the **#{position}** member to join",
            color=config.Colors.INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="permissions", description="Check user permissions")
    @app_commands.describe(user="User to check")
    async def permissions(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Check permissions"""
        user = user or interaction.user
        perms = user.guild_permissions
        key_perms = []
        if perms.administrator: key_perms.append("Administrator")
        if perms.manage_guild: key_perms.append("Manage Server")
        if perms.manage_roles: key_perms.append("Manage Roles")
        if perms.manage_channels: key_perms.append("Manage Channels")
        if perms.kick_members: key_perms.append("Kick Members")
        if perms.ban_members: key_perms.append("Ban Members")
        if perms.manage_messages: key_perms.append("Manage Messages")
        if perms.mention_everyone: key_perms.append("Mention Everyone")
        embed = discord.Embed(title=f"Permissions for {user.name}", color=user.color)
        embed.description = "\n".join(f"✅ {p}" for p in key_perms) if key_perms else "No key permissions"
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roleperms", description="Check role permissions")
    @app_commands.describe(role="Role to check")
    async def roleperms(self, interaction: discord.Interaction, role: discord.Role):
        """Role permissions"""
        perms = role.permissions
        key_perms = []
        if perms.administrator: key_perms.append("Administrator")
        if perms.manage_guild: key_perms.append("Manage Server")
        if perms.manage_roles: key_perms.append("Manage Roles")
        if perms.manage_channels: key_perms.append("Manage Channels")
        if perms.kick_members: key_perms.append("Kick Members")
        if perms.ban_members: key_perms.append("Ban Members")
        if perms.manage_messages: key_perms.append("Manage Messages")
        embed = discord.Embed(title=f"Permissions for {role.name}", color=role.color)
        embed.description = "\n".join(f"✅ {p}" for p in key_perms) if key_perms else "No key permissions"
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="compareperms", description="Compare permissions of two users")
    @app_commands.describe(user1="First user", user2="Second user")
    async def compareperms(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        """Compare permissions"""
        embed = discord.Embed(title="Permission Comparison", color=config.Colors.INFO)
        embed.add_field(name=user1.name, value=f"Admin: {user1.guild_permissions.administrator}\nMod: {user1.guild_permissions.manage_messages}")
        embed.add_field(name=user2.name, value=f"Admin: {user2.guild_permissions.administrator}\nMod: {user2.guild_permissions.manage_messages}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="activity", description="Check user activity")
    @app_commands.describe(user="User to check")
    async def activity(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """User activity"""
        user = user or interaction.user
        activity = user.activity
        embed = discord.Embed(title=f"{user.name}'s Activity", color=user.color)
        if activity:
            embed.add_field(name="Activity", value=activity.name)
            embed.add_field(name="Type", value=str(activity.type).replace("ActivityType.", ""))
        else:
            embed.description = "No activity"
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="banner", description="Get user banner")
    @app_commands.describe(user="User to check")
    async def banner(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """User banner"""
        user = user or interaction.user
        user_data = await self.bot.fetch_user(user.id)
        if user_data.banner:
            embed = discord.Embed(title=f"{user.name}'s Banner", color=user.color)
            embed.set_image(url=user_data.banner.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ User has no banner", ephemeral=True)
    
    @app_commands.command(name="badges", description="Show user badges")
    @app_commands.describe(user="User to check")
    async def badges(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """User badges"""
        user = user or interaction.user
        flags = user.public_flags
        badges = []
        if flags.staff: badges.append("Discord Staff")
        if flags.partner: badges.append("Partnered Server Owner")
        if flags.hypesquad: badges.append("HypeSquad Events")
        if flags.bug_hunter: badges.append("Bug Hunter")
        if flags.hypesquad_bravery: badges.append("HypeSquad Bravery")
        if flags.hypesquad_brilliance: badges.append("HypeSquad Brilliance")
        if flags.hypesquad_balance: badges.append("HypeSquad Balance")
        if flags.early_supporter: badges.append("Early Supporter")
        if flags.verified_bot_developer: badges.append("Verified Bot Developer")
        embed = discord.Embed(title=f"{user.name}'s Badges", color=user.color)
        embed.description = "\n".join(f"🏅 {b}" for b in badges) if badges else "No badges"
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="shared", description="Show shared servers with user")
    @app_commands.describe(user="User to check")
    async def shared(self, interaction: discord.Interaction, user: discord.User):
        """Shared servers"""
        shared = [g.name for g in self.bot.guilds if g.get_member(user.id)]
        embed = discord.Embed(title=f"Shared Servers with {user.name}", color=config.Colors.INFO)
        embed.description = "\n".join(shared[:20]) if shared else "No shared servers"
        embed.set_footer(text=f"Total: {len(shared)}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(MemberManagement(bot))
