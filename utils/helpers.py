"""
Helper functions for various bot operations
"""
import discord
import re
from datetime import datetime, timedelta
from typing import Optional, Union

def parse_time(time_str: str) -> Optional[timedelta]:
    """
    Parse a time string into a timedelta
    Examples: 1h, 30m, 1d, 1w, 1h30m
    """
    time_regex = re.compile(r'(\d+)([smhdw])')
    matches = time_regex.findall(time_str.lower())
    
    if not matches:
        return None
    
    total_seconds = 0
    for value, unit in matches:
        value = int(value)
        if unit == 's':
            total_seconds += value
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'd':
            total_seconds += value * 86400
        elif unit == 'w':
            total_seconds += value * 604800
    
    return timedelta(seconds=total_seconds)

def format_time(seconds: int) -> str:
    """Format seconds into a readable time string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"

def format_datetime(dt: datetime) -> str:
    """Format datetime into Discord timestamp"""
    return f"<t:{int(dt.timestamp())}:F>"

def format_relative_time(dt: datetime) -> str:
    """Format datetime into Discord relative timestamp"""
    return f"<t:{int(dt.timestamp())}:R>"

def replace_variables(text: str, user: discord.Member, guild: discord.Guild, channel: Optional[discord.TextChannel] = None) -> str:
    """Replace variables in custom messages"""
    replacements = {
        '{user}': user.mention,
        '{username}': user.name,
        '{server}': guild.name,
        '{members}': str(guild.member_count),
        '{channel}': channel.mention if channel else '#unknown'
    }
    
    for key, value in replacements.items():
        text = text.replace(key, value)
    
    return text

def truncate_text(text: str, max_length: int = 1024) -> str:
    """Truncate text to fit in embed field"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def get_member_status_emoji(status: discord.Status) -> str:
    """Get emoji for member status"""
    status_emojis = {
        discord.Status.online: "🟢",
        discord.Status.idle: "🟡",
        discord.Status.dnd: "🔴",
        discord.Status.offline: "⚫"
    }
    return status_emojis.get(status, "⚫")

def format_permissions(permissions: discord.Permissions) -> str:
    """Format permissions into a readable string"""
    perm_list = [perm.replace('_', ' ').title() for perm, value in permissions if value]
    return ", ".join(perm_list) if perm_list else "None"

async def get_or_fetch_user(bot: discord.Client, user_id: int) -> Optional[discord.User]:
    """Get user from cache or fetch from API"""
    user = bot.get_user(user_id)
    if user:
        return user
    
    try:
        return await bot.fetch_user(user_id)
    except discord.NotFound:
        return None

async def get_or_fetch_member(guild: discord.Guild, user_id: int) -> Optional[discord.Member]:
    """Get member from cache or fetch from API"""
    member = guild.get_member(user_id)
    if member:
        return member
    
    try:
        return await guild.fetch_member(user_id)
    except discord.NotFound:
        return None

def create_progress_bar(current: int, total: int, length: int = 20) -> str:
    """Create a text progress bar"""
    if total == 0:
        return "░" * length
    
    progress = current / total
    filled = int(length * progress)
    return "█" * filled + "░" * (length - filled)

def paginate_list(items: list, page: int = 1, per_page: int = 10) -> tuple[list, int]:
    """
    Paginate a list of items
    Returns (items_for_page, total_pages)
    """
    total_pages = (len(items) + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return items[start_idx:end_idx], total_pages

def is_url(text: str) -> bool:
    """Check if text is a URL"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(url_pattern.match(text))

def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)

def calculate_percentage(part: int, whole: int) -> float:
    """Calculate percentage"""
    if whole == 0:
        return 0.0
    return (part / whole) * 100
