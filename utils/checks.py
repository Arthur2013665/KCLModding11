"""
Permission checks and decorators for commands
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Callable

def is_admin():
    """Check if user has administrator permission"""
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)

def is_moderator():
    """Check if user has moderation permissions"""
    async def predicate(interaction: discord.Interaction) -> bool:
        perms = interaction.user.guild_permissions
        return (perms.administrator or 
                perms.kick_members or 
                perms.ban_members or 
                perms.manage_messages)
    return app_commands.check(predicate)

def has_permissions(**perms):
    """Check if user has specific permissions"""
    async def predicate(interaction: discord.Interaction) -> bool:
        user_perms = interaction.user.guild_permissions
        return all(getattr(user_perms, perm, False) for perm in perms)
    return app_commands.check(predicate)

def bot_has_permissions(**perms):
    """Check if bot has specific permissions"""
    async def predicate(interaction: discord.Interaction) -> bool:
        bot_perms = interaction.guild.me.guild_permissions
        return all(getattr(bot_perms, perm, False) for perm in perms)
    return app_commands.check(predicate)

def in_voice_channel():
    """Check if user is in a voice channel"""
    async def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.voice is not None
    return app_commands.check(predicate)

async def check_hierarchy(moderator: discord.Member, target: discord.Member) -> bool:
    """Check if moderator is higher in role hierarchy than target"""
    if moderator.guild.owner_id == moderator.id:
        return True
    if target.guild.owner_id == target.id:
        return False
    return moderator.top_role > target.top_role

async def can_execute_action(interaction: discord.Interaction, target: discord.Member, action: str) -> tuple[bool, str]:
    """
    Check if a moderation action can be executed
    Returns (can_execute, error_message)
    """
    # Check if target is bot
    if target.bot:
        return False, "❌ I cannot perform moderation actions on bots."
    
    # Check if target is self
    if target.id == interaction.user.id:
        return False, f"❌ You cannot {action} yourself."
    
    # Check if target is bot itself
    if target.id == interaction.client.user.id:
        return False, f"❌ You cannot {action} me."
    
    # Check role hierarchy
    if not await check_hierarchy(interaction.user, target):
        return False, f"❌ You cannot {action} someone with a higher or equal role."
    
    # Check if bot can perform action
    if not await check_hierarchy(interaction.guild.me, target):
        return False, f"❌ I cannot {action} someone with a higher or equal role than me."
    
    return True, ""
