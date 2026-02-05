"""
Embed builders and templates for consistent message formatting
"""
import discord
from datetime import datetime
from typing import Optional
import config

def create_embed(
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: int = config.Colors.PRIMARY,
    timestamp: bool = True
) -> discord.Embed:
    """Create a basic embed with consistent styling"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    if timestamp:
        embed.timestamp = datetime.utcnow()
    return embed

def success_embed(title: str, description: str) -> discord.Embed:
    """Create a success embed"""
    return create_embed(
        title=f"{config.Emojis.SUCCESS} {title}",
        description=description,
        color=config.Colors.SUCCESS
    )

def error_embed(title: str, description: str) -> discord.Embed:
    """Create an error embed"""
    return create_embed(
        title=f"{config.Emojis.ERROR} {title}",
        description=description,
        color=config.Colors.ERROR
    )

def warning_embed(title: str, description: str) -> discord.Embed:
    """Create a warning embed"""
    return create_embed(
        title=f"{config.Emojis.WARNING} {title}",
        description=description,
        color=config.Colors.WARNING
    )

def info_embed(title: str, description: str) -> discord.Embed:
    """Create an info embed"""
    return create_embed(
        title=f"{config.Emojis.INFO} {title}",
        description=description,
        color=config.Colors.INFO
    )

def moderation_embed(
    action: str,
    moderator: discord.Member,
    target: discord.Member,
    reason: Optional[str] = None,
    case_id: Optional[int] = None
) -> discord.Embed:
    """Create a moderation action embed"""
    embed = create_embed(
        title=f"Moderation Action: {action}",
        color=config.Colors.MODERATION
    )
    
    embed.add_field(name="User", value=f"{target.mention} ({target.id})", inline=True)
    embed.add_field(name="Moderator", value=f"{moderator.mention}", inline=True)
    
    if case_id:
        embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
    
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    else:
        embed.add_field(name="Reason", value="No reason provided", inline=False)
    
    embed.set_thumbnail(url=target.display_avatar.url)
    
    return embed

def user_info_embed(member: discord.Member) -> discord.Embed:
    """Create a user info embed"""
    embed = create_embed(
        title=f"User Information: {member.name}",
        color=member.color if member.color != discord.Color.default() else config.Colors.INFO
    )
    
    embed.set_thumbnail(url=member.display_avatar.url)
    
    # Basic info
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
    embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
    
    # Dates
    embed.add_field(
        name="Account Created",
        value=f"<t:{int(member.created_at.timestamp())}:R>",
        inline=True
    )
    embed.add_field(
        name="Joined Server",
        value=f"<t:{int(member.joined_at.timestamp())}:R>",
        inline=True
    )
    
    # Roles
    roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
    if roles:
        embed.add_field(
            name=f"Roles [{len(roles)}]",
            value=" ".join(roles) if len(roles) <= 10 else f"{' '.join(roles[:10])} and {len(roles) - 10} more",
            inline=False
        )
    
    return embed

def server_info_embed(guild: discord.Guild) -> discord.Embed:
    """Create a server info embed"""
    embed = create_embed(
        title=f"Server Information: {guild.name}",
        color=config.Colors.INFO
    )
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    # Basic info
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Owner", value=f"<@{guild.owner_id}>", inline=True)
    embed.add_field(
        name="Created",
        value=f"<t:{int(guild.created_at.timestamp())}:R>",
        inline=True
    )
    
    # Counts
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    
    # Channels breakdown
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    
    embed.add_field(name="Text Channels", value=text_channels, inline=True)
    embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
    embed.add_field(name="Categories", value=categories, inline=True)
    
    # Boost info
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
    embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
    
    return embed

def economy_embed(user: discord.Member, balance: int, level: int, xp: int, next_level_xp: int) -> discord.Embed:
    """Create an economy/profile embed"""
    embed = create_embed(
        title=f"{user.name}'s Profile",
        color=user.color if user.color != discord.Color.default() else config.Colors.PRIMARY
    )
    
    embed.set_thumbnail(url=user.display_avatar.url)
    
    embed.add_field(name=f"{config.Emojis.MONEY} Balance", value=f"${balance:,}", inline=True)
    embed.add_field(name=f"{config.Emojis.LEVEL_UP} Level", value=level, inline=True)
    embed.add_field(name="XP", value=f"{xp:,} / {next_level_xp:,}", inline=True)
    
    # Progress bar
    progress = xp / next_level_xp
    bar_length = 20
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    embed.add_field(name="Progress", value=f"`{bar}` {progress*100:.1f}%", inline=False)
    
    return embed

def leaderboard_embed(guild: discord.Guild, users: list, leaderboard_type: str) -> discord.Embed:
    """Create a leaderboard embed"""
    embed = create_embed(
        title=f"🏆 {leaderboard_type.title()} Leaderboard",
        description=f"Top users in {guild.name}",
        color=config.Colors.PRIMARY
    )
    
    medals = ["🥇", "🥈", "🥉"]
    
    for idx, user_data in enumerate(users, 1):
        medal = medals[idx-1] if idx <= 3 else f"**{idx}.**"
        
        if leaderboard_type == "balance":
            value = f"${user_data.balance:,}"
        else:  # level
            value = f"Level {user_data.level} ({user_data.xp:,} XP)"
        
        embed.add_field(
            name=f"{medal} <@{user_data.user_id}>",
            value=value,
            inline=False
        )
    
    return embed
