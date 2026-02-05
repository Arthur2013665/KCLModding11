"""
Data models for the Discord bot
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User model for economy and leveling"""
    user_id: int
    guild_id: int
    xp: int = 0
    level: int = 1
    balance: int = 0
    last_daily: Optional[datetime] = None
    last_message: Optional[datetime] = None

@dataclass
class Warning:
    """Warning model for moderation"""
    id: int
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    timestamp: datetime

@dataclass
class ModLog:
    """Moderation log model"""
    case_id: int
    guild_id: int
    action_type: str
    user_id: int
    moderator_id: int
    reason: Optional[str]
    timestamp: datetime

@dataclass
class CustomCommand:
    """Custom command model"""
    guild_id: int
    trigger: str
    response: str
    created_by: int
    created_at: datetime

@dataclass
class YouTubeSub:
    """YouTube subscription model"""
    guild_id: int
    channel_id: str
    notification_channel: int
    last_video_id: Optional[str] = None

@dataclass
class BloxFruitsAlert:
    """Blox Fruits notification model"""
    user_id: int
    guild_id: int
    fruit_name: str

@dataclass
class GuildSettings:
    """Guild settings model"""
    guild_id: int
    welcome_channel: Optional[int] = None
    welcome_message: Optional[str] = None
    goodbye_channel: Optional[int] = None
    goodbye_message: Optional[str] = None
    mod_log_channel: Optional[int] = None
    bot_log_channel: Optional[int] = None
    automod_enabled: bool = True
    spam_detection: bool = True
    blacklist_enabled: bool = True
    everyone_ping_protection: bool = True
    invite_link: Optional[str] = None

@dataclass
class AntivirusSettings:
    """KCLAntivirus settings model"""
    guild_id: int
    enabled: bool = True
    auto_lockdown: bool = False
    mod_log_channel: Optional[int] = None
    scan_attachments: bool = True
    scan_urls: bool = True
    quarantine_channel: Optional[int] = None

@dataclass
class Mute:
    """Mute model"""
    user_id: int
    guild_id: int
    unmute_at: datetime
    reason: Optional[str] = None
