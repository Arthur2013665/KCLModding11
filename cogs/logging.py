"""
Logging cog for moderation actions
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from utils.embeds import success_embed, info_embed, error_embed
from utils.checks import is_moderator
import config

class Logging(commands.Cog):
    """Moderation logging commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="modlogs", description="View moderation logs for a user")
    @app_commands.describe(user="User to view logs for")
    @is_moderator()
    async def modlogs(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """View moderation logs for a user"""
        logs = await self.bot.db.get_mod_logs(user.id, interaction.guild.id)
        
        if not logs:
            await interaction.response.send_message(
                f"✅ {user.mention} has no moderation history.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"Moderation Logs for {user.name}",
            description=f"Total actions: {len(logs)}",
            color=config.Colors.MODERATION
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        for log in logs[:10]:  # Show last 10 logs
            moderator = await self.bot.fetch_user(log.moderator_id)
            embed.add_field(
                name=f"Case #{log.case_id} - {log.action_type}",
                value=f"**Moderator:** {moderator.mention}\n**Reason:** {log.reason or 'No reason'}\n**Date:** <t:{int(log.timestamp.timestamp())}:R>",
                inline=False
            )
        
        if len(logs) > 10:
            embed.set_footer(text=f"Showing 10 of {len(logs)} logs")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="case", description="View details of a specific case")
    @app_commands.describe(case_id="Case ID to view")
    @is_moderator()
    async def case(
        self,
        interaction: discord.Interaction,
        case_id: int
    ):
        """View details of a specific moderation case"""
        log = await self.bot.db.get_mod_log_by_case(case_id)
        
        if not log:
            await interaction.response.send_message(
                f"❌ Case #{case_id} not found.",
                ephemeral=True
            )
            return
        
        user = await self.bot.fetch_user(log.user_id)
        moderator = await self.bot.fetch_user(log.moderator_id)
        
        embed = discord.Embed(
            title=f"Case #{log.case_id} - {log.action_type}",
            color=config.Colors.MODERATION,
            timestamp=log.timestamp
        )
        
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{moderator.mention}", inline=True)
        embed.add_field(name="Action", value=log.action_type, inline=True)
        embed.add_field(name="Reason", value=log.reason or "No reason provided", inline=False)
        embed.add_field(name="Date", value=f"<t:{int(log.timestamp.timestamp())}:F>", inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setmodlog", description="Set the moderation log channel")
    @app_commands.describe(channel="Channel to send moderation logs")
    @is_moderator()
    async def setmodlog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        """Set the moderation log channel"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        settings.mod_log_channel = channel.id
        await self.bot.db.update_guild_settings(settings)
        
        embed = success_embed(
            "Moderation Log Channel Set",
            f"Moderation logs will now be sent to {channel.mention}"
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setbotlog", description="Set the bot activity log channel")
    @app_commands.describe(channel="Channel to send bot activity logs")
    @is_moderator()
    async def setbotlog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        """Set the bot activity log channel"""
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        settings.bot_log_channel = channel.id
        await self.bot.db.update_guild_settings(settings)
        
        embed = success_embed(
            "🤖 Bot Log Channel Set",
            f"Bot activity logs will now be sent to {channel.mention}\n\n"
            f"**Logged events:**\n"
            f"• Bot startup/shutdown\n"
            f"• Command usage\n"
            f"• Errors and warnings\n"
            f"• Guild join/leave"
        )
        await interaction.response.send_message(embed=embed)
        
        # Send test message
        test_embed = discord.Embed(
            title="🤖 Bot Logging Enabled",
            description="Bot activity logging has been configured for this server.",
            color=config.Colors.SUCCESS
        )
        test_embed.add_field(
            name="Configured by",
            value=interaction.user.mention,
            inline=True
        )
        test_embed.add_field(
            name="Channel",
            value=channel.mention,
            inline=True
        )
        await channel.send(embed=test_embed)
    
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        """Log when a slash command is used"""
        if not interaction.guild:
            return
        
        settings = await self.bot.db.get_guild_settings(interaction.guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = interaction.guild.get_channel(settings.bot_log_channel)
        if not channel:
            return
        
        embed = discord.Embed(
            title="📝 Command Used",
            color=config.Colors.INFO,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Command", value=f"`/{command.name}`", inline=True)
        embed.add_field(name="User", value=interaction.user.mention, inline=True)
        embed.add_field(name="Channel", value=interaction.channel.mention, inline=True)
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Log command errors"""
        if not ctx.guild:
            return
        
        settings = await self.bot.db.get_guild_settings(ctx.guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = ctx.guild.get_channel(settings.bot_log_channel)
        if not channel:
            return
        
        embed = discord.Embed(
            title="⚠️ Command Error",
            description=f"```{str(error)[:500]}```",
            color=config.Colors.ERROR,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Command", value=f"`{ctx.command}`", inline=True)
        embed.add_field(name="User", value=ctx.author.mention, inline=True)
        embed.add_field(name="Channel", value=ctx.channel.mention, inline=True)
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log when a member joins"""
        settings = await self.bot.db.get_guild_settings(member.guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = member.guild.get_channel(settings.bot_log_channel)
        if not channel:
            return
        
        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} joined the server",
            color=config.Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="User", value=f"{member.name}\n{member.mention}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.set_footer(text=f"Total Members: {member.guild.member_count}")
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log when a member leaves"""
        settings = await self.bot.db.get_guild_settings(member.guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = member.guild.get_channel(settings.bot_log_channel)
        if not channel:
            return
        
        embed = discord.Embed(
            title="📤 Member Left",
            description=f"{member.mention} left the server",
            color=config.Colors.WARNING,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="User", value=f"{member.name}\n{member.mention}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Unknown", inline=True)
        embed.set_footer(text=f"Total Members: {member.guild.member_count}")
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log when a member is banned"""
        settings = await self.bot.db.get_guild_settings(guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = guild.get_channel(settings.bot_log_channel)
        if not channel:
            return
        
        # Try to get ban reason from audit log
        reason = "No reason provided"
        moderator = None
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    reason = entry.reason or "No reason provided"
                    moderator = entry.user
                    break
        except:
            pass
        
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"{user.mention} was banned from the server",
            color=config.Colors.ERROR,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User", value=f"{user.name}\n{user.mention}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        if moderator:
            embed.add_field(name="Moderator", value=moderator.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log when a member is unbanned"""
        settings = await self.bot.db.get_guild_settings(guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = guild.get_channel(settings.bot_log_channel)
        if not channel:
            return
        
        # Try to get moderator from audit log
        moderator = None
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.unban):
                if entry.target.id == user.id:
                    moderator = entry.user
                    break
        except:
            pass
        
        embed = discord.Embed(
            title="✅ Member Unbanned",
            description=f"{user.mention} was unbanned",
            color=config.Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User", value=f"{user.name}\n{user.mention}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        if moderator:
            embed.add_field(name="Moderator", value=moderator.mention, inline=True)
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log when a message is deleted"""
        if not message.guild or message.author.bot:
            return
        
        settings = await self.bot.db.get_guild_settings(message.guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = message.guild.get_channel(settings.bot_log_channel)
        if not channel or channel.id == message.channel.id:
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=config.Colors.WARNING,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        
        if message.content:
            content = message.content[:1024]
            embed.add_field(name="Content", value=content, inline=False)
        
        if message.attachments:
            embed.add_field(name="Attachments", value=f"{len(message.attachments)} file(s)", inline=True)
        
        embed.set_footer(text=f"Message ID: {message.id}")
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log when a message is edited"""
        if not before.guild or before.author.bot or before.content == after.content:
            return
        
        settings = await self.bot.db.get_guild_settings(before.guild.id)
        if not settings.bot_log_channel:
            return
        
        channel = before.guild.get_channel(settings.bot_log_channel)
        if not channel or channel.id == before.channel.id:
            return
        
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=config.Colors.INFO,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Author", value=before.author.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Before", value=before.content[:1024] if before.content else "*No content*", inline=False)
        embed.add_field(name="After", value=after.content[:1024] if after.content else "*No content*", inline=False)
        embed.add_field(name="Jump to Message", value=f"[Click here]({after.jump_url})", inline=False)
        embed.set_footer(text=f"Message ID: {before.id}")
        
        try:
            await channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Log when a channel is created"""
        settings = await self.bot.db.get_guild_settings(channel.guild.id)
        if not settings.bot_log_channel:
            return
        
        log_channel = channel.guild.get_channel(settings.bot_log_channel)
        if not log_channel:
            return
        
        # Get creator from audit log
        creator = None
        try:
            async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_create):
                if entry.target.id == channel.id:
                    creator = entry.user
                    break
        except:
            pass
        
        channel_type = str(channel.type).replace('_', ' ').title()
        
        embed = discord.Embed(
            title="📝 Channel Created",
            description=f"{channel.mention} was created",
            color=config.Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Channel", value=f"{channel.name}\n{channel.mention}", inline=True)
        embed.add_field(name="Type", value=channel_type, inline=True)
        embed.add_field(name="ID", value=channel.id, inline=True)
        if creator:
            embed.add_field(name="Created by", value=creator.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Log when a channel is deleted"""
        settings = await self.bot.db.get_guild_settings(channel.guild.id)
        if not settings.bot_log_channel:
            return
        
        log_channel = channel.guild.get_channel(settings.bot_log_channel)
        if not log_channel:
            return
        
        # Get deleter from audit log
        deleter = None
        try:
            async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    deleter = entry.user
                    break
        except:
            pass
        
        channel_type = str(channel.type).replace('_', ' ').title()
        
        embed = discord.Embed(
            title="🗑️ Channel Deleted",
            description=f"**{channel.name}** was deleted",
            color=config.Colors.ERROR,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Channel", value=channel.name, inline=True)
        embed.add_field(name="Type", value=channel_type, inline=True)
        embed.add_field(name="ID", value=channel.id, inline=True)
        if deleter:
            embed.add_field(name="Deleted by", value=deleter.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Log when a role is created"""
        settings = await self.bot.db.get_guild_settings(role.guild.id)
        if not settings.bot_log_channel:
            return
        
        log_channel = role.guild.get_channel(settings.bot_log_channel)
        if not log_channel:
            return
        
        # Get creator from audit log
        creator = None
        try:
            async for entry in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_create):
                if entry.target.id == role.id:
                    creator = entry.user
                    break
        except:
            pass
        
        embed = discord.Embed(
            title="🎭 Role Created",
            description=f"{role.mention} was created",
            color=role.color if role.color != discord.Color.default() else config.Colors.SUCCESS,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Role", value=f"{role.name}\n{role.mention}", inline=True)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        if creator:
            embed.add_field(name="Created by", value=creator.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Log when a role is deleted"""
        settings = await self.bot.db.get_guild_settings(role.guild.id)
        if not settings.bot_log_channel:
            return
        
        log_channel = role.guild.get_channel(settings.bot_log_channel)
        if not log_channel:
            return
        
        # Get deleter from audit log
        deleter = None
        try:
            async for entry in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    deleter = entry.user
                    break
        except:
            pass
        
        embed = discord.Embed(
            title="🗑️ Role Deleted",
            description=f"**{role.name}** was deleted",
            color=config.Colors.ERROR,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Role", value=role.name, inline=True)
        embed.add_field(name="ID", value=role.id, inline=True)
        if deleter:
            embed.add_field(name="Deleted by", value=deleter.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        """Log when a role is updated"""
        if before.name == after.name and before.color == after.color and before.permissions == after.permissions:
            return  # No significant changes
        
        settings = await self.bot.db.get_guild_settings(after.guild.id)
        if not settings.bot_log_channel:
            return
        
        log_channel = after.guild.get_channel(settings.bot_log_channel)
        if not log_channel:
            return
        
        # Get updater from audit log
        updater = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_update):
                if entry.target.id == after.id:
                    updater = entry.user
                    break
        except:
            pass
        
        embed = discord.Embed(
            title="🎭 Role Updated",
            description=f"{after.mention} was updated",
            color=after.color if after.color != discord.Color.default() else config.Colors.INFO,
            timestamp=discord.utils.utcnow()
        )
        
        changes = []
        if before.name != after.name:
            changes.append(f"**Name:** {before.name} → {after.name}")
        if before.color != after.color:
            changes.append(f"**Color:** {before.color} → {after.color}")
        if before.permissions != after.permissions:
            changes.append("**Permissions:** Updated")
        
        if changes:
            embed.add_field(name="Changes", value="\n".join(changes), inline=False)
        
        if updater:
            embed.add_field(name="Updated by", value=updater.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log when a member's roles are updated"""
        # Only log role changes
        if before.roles == after.roles:
            return
        
        settings = await self.bot.db.get_guild_settings(after.guild.id)
        if not settings.bot_log_channel:
            return
        
        log_channel = after.guild.get_channel(settings.bot_log_channel)
        if not log_channel:
            return
        
        # Get role changes
        added_roles = [role for role in after.roles if role not in before.roles]
        removed_roles = [role for role in before.roles if role not in after.roles]
        
        if not added_roles and not removed_roles:
            return
        
        # Get moderator from audit log
        moderator = None
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id:
                    moderator = entry.user
                    break
        except:
            pass
        
        embed = discord.Embed(
            title="👤 Member Roles Updated",
            description=f"{after.mention}'s roles were changed",
            color=config.Colors.INFO,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=after.display_avatar.url)
        embed.add_field(name="Member", value=after.mention, inline=True)
        
        if added_roles:
            embed.add_field(
                name="➕ Roles Added",
                value=", ".join([role.mention for role in added_roles]),
                inline=False
            )
        
        if removed_roles:
            embed.add_field(
                name="➖ Roles Removed",
                value=", ".join([role.mention for role in removed_roles]),
                inline=False
            )
        
        if moderator:
            embed.add_field(name="Changed by", value=moderator.mention, inline=True)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass

async def setup(bot):
    await bot.add_cog(Logging(bot))
